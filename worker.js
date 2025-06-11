const tgBotToken = 'توکن_ربات_تلگرام';
const tgChannel = '@channel_or_group_username'; // مثلا @mychannel
const symbol = 'USDTIRT'; // یا BTCIRT و هر جفت ارزی که بخوای

export default {
  async fetch(request, env, ctx) {
    const apiUrl = `https://api.nobitex.ir/v2/orderbook/${symbol}`;
    try {
      const response = await fetch(apiUrl);
      const data = await response.json();
      const price = data?.lastTradePrice;

      if (!price) {
        return new Response("Failed to get price", { status: 500 });
      }
      console.log(`Retrieved price for ${symbol}: ${price}`);

      const lastPrice = await env.gheymat_link.get(symbol);

      if (lastPrice !== price) {
        console.log(`Price changed for ${symbol}. Old: ${lastPrice}, New: ${price}. Sending update.`);
        const message = `💸 قیمت لحظه‌ای ${symbol} در نوبیتکس: ${price} تومان`;
        await sendToTelegram(tgBotToken, tgChannel, message);
        await env.gheymat_link.put(symbol, price);
      } else {
        console.log(`Price for ${symbol} remains ${lastPrice}. No update needed.`);
      }

      console.log("Successfully checked and updated price for " + symbol);
      return new Response("Price checked and updated", { status: 200 });

    } catch (err) {
      console.error(`Error in fetch function for ${symbol}: `, err);
      return new Response(`Error: ${err.message}`, { status: 500 });
    }
  }
}

async function sendToTelegram(botToken, chatId, message) {
  const url = `https://api.telegram.org/bot${botToken}/sendMessage`;
  try {
    await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: chatId,
        text: message,
        parse_mode: "HTML"
      })
    });
  } catch (error) {
    console.error("Error sending message to Telegram:", error);
  }
}
