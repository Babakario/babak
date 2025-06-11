// Define the list of coin pairs you want to watch
const COIN_PAIRS_TO_WATCH = ['USDT-RLS', 'BTC-RLS', 'ETH-RLS']; // Example list

async function getNobitexPrice(coinPair) {
  const apiUrl = 'https://api.nobitex.ir/v2/orderbook/all';
  try {
    const response = await fetch(apiUrl);
    if (!response.ok) {
      // Include coinPair in the error message thrown
      throw new Error(`Nobitex API request failed with status: ${response.status} for ${coinPair}`);
    }
    const data = await response.json();
    const marketData = data[coinPair];

    if (marketData && marketData.status === 'active') {
      const price = parseFloat(marketData.latest);
      if (isNaN(price)) {
        if (marketData.bids && marketData.bids.length > 0) {
          const bestBid = parseFloat(marketData.bids[0][0]);
          if (!isNaN(bestBid)) return bestBid;
        }
        // Return error string for this specific coin
        return `Error: Price for ${coinPair} is not available or invalid.`;
      }
      return price;
    } else {
      // Return error string for this specific coin
      return `Error: Market ${coinPair} not found or is not active on Nobitex.`;
    }
  } catch (error) {
    // Log the specific coin pair in the error message
    console.error(`Error fetching Nobitex price for ${coinPair}:`, error.message);
    // Return a specific error string or object to indicate failure for this coin
    return `Error: ${error.message}`;
  }
}

async function sendTelegramMessage(messageText, env) {
  if (!env.TELEGRAM_BOT_TOKEN || !env.TELEGRAM_CHAT_ID) {
    console.error('Telegram token or chat ID not set in env. Cannot send message.');
    // Return a value indicating failure or simply log and return if this function is called without pre-checks.
    // The primary check is now in processCoinPrices.
    return { success: false, error: 'Telegram secrets not configured.' };
  }
  const telegramUrl = `https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`;
  const payload = {
    chat_id: env.TELEGRAM_CHAT_ID,
    text: messageText,
    parse_mode: 'HTML',
  };

  try {
    const response = await fetch(telegramUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ description: "Failed to parse Telegram error response" }));
      const errorMessage = `Telegram API request failed: ${response.status} ${response.statusText} - ${errorData.description || JSON.stringify(errorData)}`;
      console.error(errorMessage);
      return { success: false, error: errorMessage };
    }
    console.log('Message sent to Telegram successfully.');
    return { success: true, data: await response.json() };
  } catch (error) {
    console.error('Error sending message to Telegram:', error.message);
    return { success: false, error: error.message };
  }
}

async function processCoinPrices(env, source) { // source is 'Manual Test' or 'Scheduled'
  if (!env.TELEGRAM_BOT_TOKEN || !env.TELEGRAM_CHAT_ID) {
    const errorMsg = `${source}: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set in Cloudflare environment variables.`;
    console.error(errorMsg);
    // For fetch, this critical error should be returned to the client.
    // For scheduled, it's logged, and we can't do much more.
    return { success: false, message: errorMsg, isCriticalError: true };
  }

  let messageLines = [`<b>Nobitex Price Update (${source}):</b>`];
  let overallSuccess = true; // Tracks if all coin prices were fetched successfully

  for (const coinPair of COIN_PAIRS_TO_WATCH) {
    const priceResult = await getNobitexPrice(coinPair);
    if (typeof priceResult === 'number') {
      messageLines.push(`<b>${coinPair}:</b> ${priceResult} RLS`);
    } else {
      // priceResult here is an error message string from getNobitexPrice
      messageLines.push(`<b>${coinPair}:</b> ${priceResult}`);
      overallSuccess = false; // Mark that at least one coin failed
    }
  }

  const fullMessage = messageLines.join('\n'); // Using newline character for Telegram formatting

  const telegramResult = await sendTelegramMessage(fullMessage, env);

  if (telegramResult.success) {
    console.log(`${source} task: Successfully sent price updates to Telegram.`);
    // If overallSuccess is false, it means some coin data was erroneous, but message was sent.
    return { success: overallSuccess, message: fullMessage, telegramSent: true };
  } else {
    console.error(`${source} task: Failed to send message to Telegram. Error: ${telegramResult.error}`);
    // Attempt to send a simplified error message to Telegram about the failure to send the main message
    const simplifiedErrorMsg = `${source}: Critical error - Could not send price updates to Telegram. Check worker logs. Last error: ${telegramResult.error}`;
    await sendTelegramMessage(simplifiedErrorMsg, env); // Fire and forget for this fallback
    return { success: false, message: simplifiedErrorMsg, telegramSent: false, isCriticalError: !overallSuccess };
  }
}


export default {
  async fetch(request, env, ctx) {
    const result = await processCoinPrices(env, 'Manual Test');

    if (result.isCriticalError) {
        // This typically means Telegram secrets are missing.
        return new Response(result.message, { status: 500 });
    }

    if (result.telegramSent) {
      // Message (even with partial errors) was sent to Telegram.
      // The 'success' field in result reflects if all coin prices were fetched successfully.
      const status = result.success ? 200 : 207; // 207 Multi-Status if some prices failed
      return new Response(result.message, { status: status, headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
    } else {
      // Failed to send any message to Telegram (e.g., Telegram API down or bad token)
      return new Response(`Error: Could not send message to Telegram. ${result.message}`, { status: 500 });
    }
  },
  async scheduled(event, env, ctx) {
    console.log('Scheduled event triggered. Processing coin prices...');
    const result = await processCoinPrices(env, 'Scheduled');
    if (result.success && result.telegramSent) {
        console.log('Scheduled task finished successfully. Price updates sent.');
    } else if (result.telegramSent === false) {
        console.error('Scheduled task: CRITICAL - Failed to send message to Telegram.');
    } else {
        console.warn('Scheduled task finished. Some coin prices could not be fetched, but the report was sent to Telegram.');
    }
    // Scheduled tasks don't return a Response object. Logging is key.
  },
};
