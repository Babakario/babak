// Environment Variables available in 'env':
// env.TOKEN: Telegram Bot Token
// env.ADMINS: Comma-separated string of admin Telegram User IDs
// env.ZARINPAL_MERCHANT_ID: Zarinpal Merchant ID
// env.bot_values_link: Cloudflare KV Namespace binding
// env.dblink: Cloudflare D1 Database binding

addEventListener('fetch', event => {
  // Pass env to handleRequest, and event for event.waitUntil
  event.respondWith(handleRequest(event.request, event.env, event));
});

async function handleRequest(request, env, event) {
  const url = new URL(request.url);
  const path = url.pathname;

  if (path === `/bot${env.TOKEN}`) {
    if (request.method === 'POST') {
      const update = await request.json();
      // Ensure async operations complete after responding to Telegram
      event.waitUntil(handleTelegramUpdate(update, env, event));
      return new Response('OK', { status: 200 });
    } else {
      return new Response('Method Not Allowed', { status: 405 });
    }
  } else if (path === '/init') {
    try {
      const workerUrl = `https://${url.hostname}`;
      const webhookUrl = `${workerUrl}/bot${env.TOKEN}`;
      const setWebhookUrl = `https://api.telegram.org/bot${env.TOKEN}/setWebhook?url=${encodeURIComponent(webhookUrl)}&drop_pending_updates=true`;
      const response = await fetch(setWebhookUrl);
      const result = await response.json();
      if (result.ok) {
        return new Response(`Webhook set successfully to ${webhookUrl}!`, { status: 200 });
      } else {
        return new Response(`Webhook setup failed: ${result.description}`, { status: 500 });
      }
    } catch (error) {
      console.error("Error setting webhook:", error);
      return new Response(`Error setting webhook: ${error.message}`, { status: 500 });
    }
  } else if (path.startsWith('/zarinpal_callback')) {
    event.waitUntil(handleZarinpalCallback(request, env)); // Pass env
    return new Response('Zarinpal callback received', { status: 200 });
  } else {
    return new Response('Not Found', { status: 404 });
  }
}

// --- Admin Check ---
function isAdmin(userId, env) {
  const adminIds = (env.ADMINS || "").split(',').map(id => String(id).trim());
  return adminIds.includes(String(userId));
}

// --- Telegram API Helper Functions ---
async function sendMessage(chatId, text, env, parseMode = null, replyMarkup = null) {
  const url = `https://api.telegram.org/bot${env.TOKEN}/sendMessage`;
  const payload = { chat_id: chatId, text: text };
  if (parseMode) payload.parse_mode = parseMode;
  if (replyMarkup) payload.reply_markup = replyMarkup;

  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return response.json();
}

async function forwardMessage(chatId, fromChatId, messageId, env) {
  const url = `https://api.telegram.org/bot${env.TOKEN}/forwardMessage`;
  const payload = { chat_id: chatId, from_chat_id: fromChatId, message_id: messageId };
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return response.json();
}

async function answerCallbackQuery(callbackQueryId, env, text = null, showAlert = false) {
  const url = `https://api.telegram.org/bot${env.TOKEN}/answerCallbackQuery`;
  const payload = { callback_query_id: callbackQueryId };
  if (text) payload.text = text;
  payload.show_alert = showAlert;

  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return response.json();
}

// --- Utility Functions ---
function generateRandomKey(length = 16) {
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * characters.length));
  }
  return result;
}

// --- Main Handler Functions ---
async function handleTelegramUpdate(update, env, event) {
  console.log("Received Telegram update:", JSON.stringify(update, null, 2));

  if (update.message) {
    const message = update.message;
    const chatId = message.chat.id;
    const userId = message.from.id;
    const text = message.text || "";

    // Clear admin states on /start or /newfile
    if (isAdmin(userId, env) && (text === '/start' || text === '/newfile')) {
        await env.bot_values_link.delete(`state:${userId}`);
        await env.bot_values_link.delete(`pending_file_info:${userId}`);
    }

    const userState = await env.bot_values_link.get(`state:${userId}`);

    if (isAdmin(userId, env)) {
      if (text === '/newfile') {
        await env.bot_values_link.put(`state:${userId}`, 'admin_awaiting_file');
        await sendMessage(chatId, "Hello Admin! Please send the file you want to sell.", env);
        return;
      }

      if (userState === 'admin_awaiting_file') {
        let fileId = null; let fileType = null;
        if (message.document) { fileId = message.document.file_id; fileType = 'document'; }
        else if (message.photo && message.photo.length > 0) { fileId = message.photo[message.photo.length - 1].file_id; fileType = 'photo';}
        else if (message.video) { fileId = message.video.file_id; fileType = 'video'; }
        else if (message.audio) { fileId = message.audio.file_id; fileType = 'audio'; }

        if (fileId) {
          await env.bot_values_link.put(`pending_file_info:${userId}`, JSON.stringify({ file_id: fileId, from_chat_id: String(chatId), type: fileType }));
          await env.bot_values_link.put(`state:${userId}`, 'admin_awaiting_price');
          await sendMessage(chatId, "File received. Now, enter the price (e.g., 10000 for Toman).", env);
        } else {
          await sendMessage(chatId, "No file received. Please send a document, photo, video, or audio.", env);
        }
        return;
      }

      if (userState === 'admin_awaiting_price') {
        const price = parseInt(text);
        if (isNaN(price) || price <= 0) {
          await sendMessage(chatId, "Invalid price. Please enter a positive number.", env);
          return;
        }
        const pendingInfoStr = await env.bot_values_link.get(`pending_file_info:${userId}`);
        if (pendingInfoStr) {
          const pendingInfo = JSON.parse(pendingInfoStr);
          pendingInfo.price = price;
          await env.bot_values_link.put(`pending_file_info:${userId}`, JSON.stringify(pendingInfo));
          await env.bot_values_link.put(`state:${userId}`, 'admin_awaiting_caption');
          await sendMessage(chatId, `Price set to ${price}. Now, enter a caption for this file.`, env);
        } else {
          await sendMessage(chatId, "Error: No pending file info. Start over with /newfile.", env);
          await env.bot_values_link.delete(`state:${userId}`);
        }
        return;
      }

      if (userState === 'admin_awaiting_caption') {
        const caption = text;
        const pendingInfoStr = await env.bot_values_link.get(`pending_file_info:${userId}`);
        if (pendingInfoStr) {
          const pendingInfo = JSON.parse(pendingInfoStr);
          try {
            const uniqueFileId = `file_${generateRandomKey(10)}`;
            // D1 files table: id (PK, auto-inc), unique_id, message_id (TG file_id), from_chat_id, caption, price, file_type
            const stmt = env.dblink.prepare(
              "INSERT INTO files (unique_id, message_id, from_chat_id, caption, price, file_type) VALUES (?, ?, ?, ?, ?, ?)"
            );
            // Ensure from_chat_id is stored as string if it comes from message.chat.id which is number
            await stmt.bind(uniqueFileId, pendingInfo.file_id, String(pendingInfo.from_chat_id), caption, pendingInfo.price, pendingInfo.type).run();

            await sendMessage(chatId, `File saved!\nUser-facing ID: ${uniqueFileId}\nPrice: ${pendingInfo.price}\nCaption: ${caption}`, env);
          } catch (d1Error) {
            console.error("D1 Error (Admin /newfile):", d1Error);
            await sendMessage(chatId, `Error saving file: ${d1Error.message}. Check logs.`, env);
          } finally {
            await env.bot_values_link.delete(`state:${userId}`);
            await env.bot_values_link.delete(`pending_file_info:${userId}`);
          }
        } else {
          await sendMessage(chatId, "Error: No pending file info. Start over with /newfile.", env);
          await env.bot_values_link.delete(`state:${userId}`);
        }
        return;
      }
    } // End of isAdmin block

    // --- Regular User Commands ---
    if (text === '/start') {
      const welcomeMessage = "Welcome! Use /buy <FILE_ID> to purchase a file.";
      await sendMessage(chatId, welcomeMessage, env);
    } else if (text.startsWith('/buy ')) {
        const fileUniqueIdToBuy = text.split(' ')[1];
        if (!fileUniqueIdToBuy) {
            await sendMessage(chatId, "Usage: /buy <FILE_ID>", env);
            return;
        }

        try {
            // files table: id (db_file_id), unique_id, caption, price
            const fileStmt = env.dblink.prepare("SELECT id, caption, price FROM files WHERE unique_id = ?");
            const fileToBuy = await fileStmt.bind(fileUniqueIdToBuy).first();

            if (fileToBuy) {
                const db_file_id = fileToBuy.id; // This is files.id (auto-incremented PK)
                const price = fileToBuy.price;
                const caption = fileToBuy.caption;
                const buyerUserId = String(userId);

                // orders table: id (PK, auto-inc), userid (buyer's TG ID), fileid (files.id), status, random_key,
                //               payment_amount, zarinpal_authority, zarinpal_ref_id, payment_data, payment_timestamp
                const orderRandomKey = `orderkey_${generateRandomKey(12)}`; // Generate a random key for the order
                const orderStmt = env.dblink.prepare(
                    "INSERT INTO orders (userid, fileid, status, payment_amount, random_key) VALUES (?, ?, 0, ?, ?)"
                );
                // D1 run() returns D1Result, last_row_id is in meta
                const d1OrderInsertResult = await orderStmt.bind(buyerUserId, db_file_id, price, orderRandomKey).run();

                const d1_order_id = d1OrderInsertResult.meta.last_row_id;
                if (!d1_order_id) {
                    await sendMessage(chatId, "Database error creating order. Please try again.", env);
                    console.error("Failed to get last_row_id for order. File unique_id:", fileUniqueIdToBuy);
                    return;
                }

                const callbackInfo = { userChatId: String(chatId), db_file_id: db_file_id, price: price, d1_order_id: d1_order_id };
                await env.bot_values_link.put(`order_payment_info:${d1_order_id}`, JSON.stringify(callbackInfo), { expirationTtl: 3600 }); // 1 hour

                const currentHostname = new URL(request.url).hostname; // Get hostname for callback
                const callbackURL = `https://${currentHostname}/zarinpal_callback?order_id=${d1_order_id}`;

                const zarinpalRequestBody = {
                    merchant_id: env.ZARINPAL_MERCHANT_ID,
                    amount: price * 10, // Rials
                    description: `Payment for: ${caption} (Order: ${d1_order_id})`,
                    callback_url: callbackURL,
                    metadata: { userId: buyerUserId, file_unique_id: fileUniqueIdToBuy, d1_order_id: d1_order_id }
                };

                const zpResponse = await fetch('https://api.zarinpal.com/pg/v4/payment/request.json', {
                    method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                    body: JSON.stringify(zarinpalRequestBody)
                });
                const zpResult = await zpResponse.json();

                if (zpResult.data && zpResult.data.authority) {
                    await env.dblink.prepare("UPDATE orders SET zarinpal_authority = ? WHERE id = ?")
                                     .bind(zpResult.data.authority, d1_order_id).run();
                    const paymentLink = `https://www.zarinpal.com/pg/StartPay/${zpResult.data.authority}`;
                    const keyboard = { inline_keyboard: [[{ text: "Pay Now 💳", url: paymentLink }]] };
                    await sendMessage(chatId, `Purchase "${caption}" for ${price} Toman:`, env, null, keyboard);
                } else {
                    const errorMsg = zpResult.errors?.message || JSON.stringify(zpResult.errors) || 'Unknown Zarinpal error';
                    await sendMessage(chatId, `Zarinpal error: ${errorMsg}. Try again.`, env);
                    // Optionally mark order as failed in D1 here
                }
            } else {
                await sendMessage(chatId, `File ID "${fileUniqueIdToBuy}" not found.`, env);
            }
        } catch (e) {
            console.error("Error during /buy processing:", e);
            await sendMessage(chatId, "An error occurred. Please try again later.", env);
        }
    } else if (!isAdmin(userId, env) && text && !text.startsWith('/')) {
        await sendMessage(chatId, "Unknown command. Use /start or /buy <FILE_ID>.", env);
    }
  } else if (update.callback_query) {
    await handleCallbackQuery(update.callback_query, env, event);
  }
}

async function handleCallbackQuery(query, env, event) {
  const queryId = query.id;
  const data = query.data;
  const message = query.message;
  const chatId = message.chat.id;

  await answerCallbackQuery(queryId, env);

  if (data === 'help') {
    const helpText = `Use /buy <FILE_ID> to purchase a file.\nAdmins: /newfile to add files.`;
    await sendMessage(chatId, helpText, env);
  } else {
    await sendMessage(chatId, `Action processed. (Data: ${data})`, env);
  }
}

async function handleZarinpalCallback(request, env) {
  const url = new URL(request.url);
  const params = url.searchParams;
  const status = params.get('Status');
  const authority = params.get('Authority');
  const d1_order_id_str = params.get('order_id'); // This is D1 orders.id as string

  if (!d1_order_id_str) {
    console.error("Zarinpal callback: No order_id (d1_order_id) found.");
    return new Response("Error: Missing order_id", { status: 400 });
  }
  const d1_order_id = parseInt(d1_order_id_str);


  const paymentInfoStr = await env.bot_values_link.get(`order_payment_info:${d1_order_id}`);
  if (!paymentInfoStr) {
    console.error(`Zarinpal callback: No payment info in KV for d1_order_id ${d1_order_id}. Expired or invalid.`);
    return new Response("Error: Invalid or expired order information", { status: 400 });
  }
  const paymentInfo = JSON.parse(paymentInfoStr); // { userChatId, db_file_id, price, d1_order_id }
  const userChatId = paymentInfo.userChatId; // This is a string

  try {
    if (status === 'OK' && authority) {
      const verificationBody = {
        merchant_id: env.ZARINPAL_MERCHANT_ID,
        amount: paymentInfo.price * 10, // Rials
        authority: authority,
      };

      const verifyResponse = await fetch('https://api.zarinpal.com/pg/v4/payment/verify.json', {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(verificationBody),
      });
      const verifyResult = await verifyResponse.json();
      const paymentDataJson = JSON.stringify(verifyResult); // Store full Zarinpal response

      if (verifyResult.data && (verifyResult.data.code === 100 || verifyResult.data.code === 101)) { // 100: Success, 101: Already verified
        const ref_id = verifyResult.data.ref_id;

        await env.dblink.prepare(
          "UPDATE orders SET status = 1, zarinpal_ref_id = ?, payment_data = ?, payment_timestamp = datetime('now') WHERE id = ?"
        ).bind(ref_id, paymentDataJson, d1_order_id).run();

        // Log to payment_history table
        // Schema: id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER, payment_data TEXT, payment_date TEXT
        try {
            const paymentDate = new Date().toISOString();
            await env.dblink.prepare(
                "INSERT INTO payment_history (order_id, payment_data, payment_date) VALUES (?, ?, ?)"
            ).bind(d1_order_id, paymentDataJson, paymentDate).run();
        } catch (phError) {
            console.error("Error logging to payment_history:", phError);
            // Non-critical error, so don't stop the user flow, but log it.
        }

        await sendMessage(userChatId, `Payment successful for Order ID ${d1_order_id}!\nRef ID: ${ref_id}`, env);

        const fileStmt = env.dblink.prepare("SELECT message_id, from_chat_id, caption FROM files WHERE id = ?");
        const fileRecord = await fileStmt.bind(paymentInfo.db_file_id).first();

        if (fileRecord) {
            await sendMessage(userChatId, `Your file "${fileRecord.caption}" is being sent:`, env);
            // Ensure from_chat_id and message_id are correct type for forwardMessage
            await forwardMessage(userChatId, String(fileRecord.from_chat_id), String(fileRecord.message_id), env);
        } else {
            await sendMessage(userChatId, `File details not found post-payment (Order ${d1_order_id}). Contact admin.`, env);
            console.error(`File (files.id ${paymentInfo.db_file_id}) not found after payment for order ${d1_order_id}.`);
        }
      } else {
        const errorCode = verifyResult.errors?.code || verifyResult.data?.code || 'N/A';
        const errorMsgForUser = `Payment verification failed (Order ${d1_order_id}). Error: ${errorCode}.`;
        await env.dblink.prepare(
            "UPDATE orders SET status = 2, zarinpal_ref_id = ?, payment_data = ? WHERE id = ?"
        ).bind(`VERIFY_FAILED_${errorCode}`, paymentDataJson, d1_order_id).run();
        await sendMessage(userChatId, errorMsgForUser, env);
        console.error("Zarinpal verification error:", paymentDataJson);
      }
    } else { // Payment not OK (cancelled by user, or other Zarinpal issue before verification page)
      await env.dblink.prepare("UPDATE orders SET status = 2, zarinpal_authority = ? WHERE id = ?")
                       .bind(`STATUS_${status}_NO_AUTHORITY`, d1_order_id).run();
      await sendMessage(userChatId, `Payment for Order ID ${d1_order_id} not completed (Status: ${status}).`, env);
    }
  } catch (e) {
      await sendMessage(userChatId, `System error processing payment for Order ${d1_order_id}. Contact support.`, env);
      console.error("Error in handleZarinpalCallback:", e, e.stack);
      try { // Attempt to mark order as system error
        await env.dblink.prepare("UPDATE orders SET status = 3, payment_data = ? WHERE id = ?")
                         .bind(JSON.stringify({ error: e.message }), d1_order_id).run();
      } catch (dbErr) { console.error("Failed to update order to system error state:", dbErr); }
  } finally {
      await env.bot_values_link.delete(`order_payment_info:${d1_order_id}`);
  }
  return new Response("Callback processed", { status: 200 });
}
