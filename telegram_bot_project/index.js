require('dotenv').config(); // Must be at the very top
const TelegramBot = require('node-telegram-bot-api');
const ethers = require('ethers');
const cron = require('node-cron');
const dbManager = require('./database');

const token = process.env.TELEGRAM_BOT_TOKEN;
if (!token) {
  console.error("TELEGRAM_BOT_TOKEN not found in .env file. Please set it.");
  process.exit(1);
}
const ADMIN_TELEGRAM_ID = process.env.ADMIN_TELEGRAM_ID || '0'; // Default to '0' if not set

// Create a bot that uses 'polling' to fetch new updates
const bot = new TelegramBot(token, {polling: true});

// Helper function to check if a user is an admin
const isAdmin = (userId) => userId.toString() === ADMIN_TELEGRAM_ID;

// Store prompted users for wallet connection (still needed for flow control)
const promptedUsers = new Set();

// Main bot logic wrapped in an async IIFE to allow await for DB connection
(async () => {
  try {
    await dbManager.connectDB();
    await dbManager.initializeDefaultTasks();
    console.log('Database connected and default tasks initialized.');
  } catch (error) {
    console.error("Initialization error:", error);
    process.exit(1);
  }

  // Listen for /start command
  bot.onText(/\/start/, async (msg) => {
    const chatId = msg.chat.id;
    const userId = msg.from.id;
    try {
      let user = await dbManager.getUser(userId);
      if (!user) {
        user = await dbManager.createUser(userId);
        bot.sendMessage(chatId, 'Welcome to the Web3 Airdrop Bot! Your profile has been created.');
      } else {
        bot.sendMessage(chatId, 'Welcome back to the Web3 Airdrop Bot!');
      }
    } catch (error) {
      console.error("Error in /start handler:", error);
      bot.sendMessage(chatId, 'An error occurred. Please try again later.');
    }
  });

  // Listen for /connectwallet command
  bot.onText(/\/connectwallet/, async (msg) => {
    const chatId = msg.chat.id;
    const userId = msg.from.id;
    try {
      // Ensure user exists
      let user = await dbManager.getUser(userId);
      if (!user) {
        user = await dbManager.createUser(userId);
      }
      bot.sendMessage(chatId, 'Please reply with your Ethereum wallet address starting with 0x...');
      promptedUsers.add(userId); // Use userId to track prompts
    } catch (error) {
      console.error("Error in /connectwallet handler:", error);
      bot.sendMessage(chatId, 'An error occurred. Please try again later.');
    }
  });

  // Listen for /tasks command
  bot.onText(/\/tasks/, async (msg) => {
    const chatId = msg.chat.id;
    const userId = msg.from.id;
    try {
      // const allTasks = await dbManager.getAllTasks(); // Old: gets all tasks
      const dailyActiveTasks = await dbManager.getDailyActiveTasks(); // New: gets only daily active tasks
      const completedUserTaskIds = await dbManager.getUserCompletedTasks(userId);

      if (dailyActiveTasks.length === 0) {
        bot.sendMessage(chatId, "No daily tasks available at the moment. Please check back later!");
        return;
      }

      let tasksMessage = "✨ Daily Tasks ✨\n\n";
      dailyActiveTasks.forEach(task => {
        const isCompleted = completedUserTaskIds.includes(task.customId);
        const icon = isCompleted ? "✅" : "☑️";
        // Display customId for the /complete command
        tasksMessage += `${icon} ${task.description} - ${task.rewardPoints} points (ID: ${task.customId})\n`;
      });

      bot.sendMessage(chatId, tasksMessage);
    } catch (error) {
      console.error("Error in /tasks handler:", error);
      bot.sendMessage(chatId, 'An error occurred while fetching tasks. Please try again later.');
    }
  });

  // Listen for /complete <custom_task_id> command
  // Regex updated to match alphanumeric custom IDs with potential underscores/hyphens
  bot.onText(/\/complete ([a-zA-Z0-9_-]+)/, async (msg, match) => {
    const chatId = msg.chat.id;
    const userId = msg.from.id;
    const customTaskIdToComplete = match[1];

    try {
      const taskToComplete = await dbManager.getTask(customTaskIdToComplete);

      if (!taskToComplete) {
        bot.sendMessage(chatId, `Invalid Task ID: ${customTaskIdToComplete}. Please check the ID from the /tasks list.`);
        return;
      }

      const completedUserTaskIds = await dbManager.getUserCompletedTasks(userId);
      if (completedUserTaskIds.includes(customTaskIdToComplete)) {
        bot.sendMessage(chatId, `Task "${taskToComplete.description}" is already marked as complete.`);
        return;
      }

      // Ensure user exists before trying to complete task (though /start should handle this)
      let user = await dbManager.getUser(userId);
      if (!user) {
        user = await dbManager.createUser(userId);
      }

      await dbManager.completeTaskForUser(userId, customTaskIdToComplete);
      // Here you might also add points to the user
      // await dbManager.updateUserPoints(userId, taskToComplete.rewardPoints);
      bot.sendMessage(chatId, `Task "${taskToComplete.description}" marked as complete!`);
      console.log(`Task ${customTaskIdToComplete} marked complete for user ${userId}`);
    } catch (error) {
      console.error("Error in /complete handler:", error);
      bot.sendMessage(chatId, 'An error occurred while completing the task. Please try again later.');
    }
  });

  // Listen for messages (for wallet address)
  bot.on('message', async (msg) => {
    const chatId = msg.chat.id;
    const userId = msg.from.id; // Get userId from the message object
    const text = msg.text;

    if (!text) return; // Ignore messages without text (e.g. stickers, photos)

    // Ignore commands if not part of a specific flow like wallet connect
    if (text.startsWith('/') && !promptedUsers.has(userId)) {
      return;
    }

    if (text.startsWith('/') && promptedUsers.has(userId)) {
       // User sent a command while prompted, maybe they changed their mind.
       // For now, let other command handlers pick it up.
       // We could also remove them from promptedUsers here if desired.
    }

    // Check if the user (by userId) was prompted for a wallet address
    if (promptedUsers.has(userId) && !text.startsWith('/')) { // Ensure it's not a command
      if (text.startsWith('0x') && ethers.utils.isAddress(text)) { // Use ethers for robust validation
        try {
          await dbManager.updateUserWallet(userId, text);
          bot.sendMessage(chatId, `Wallet address ${text} received and saved.`);
          console.log(`Received wallet address: ${text} from user ID: ${userId}`);
          promptedUsers.delete(userId);

          // Auto-complete WALLET_CONNECT task
          const allTasks = await dbManager.getAllTasks();
          const walletTask = allTasks.find(t => t.type === 'WALLET_CONNECT');
          if (walletTask) {
            const completedUserTaskIds = await dbManager.getUserCompletedTasks(userId);
            if (!completedUserTaskIds.includes(walletTask.customId)) {
              await dbManager.completeTaskForUser(userId, walletTask.customId);
              // Optionally add points here too
              // await dbManager.updateUserPoints(userId, walletTask.rewardPoints);
              bot.sendMessage(chatId, `Your '${walletTask.description}' task is now marked as complete!`);
              console.log(`Task ${walletTask.customId} (WALLET_CONNECT) automatically marked complete for user ${userId}`);
            }
          }
        } catch (error) {
          console.error("Error processing wallet address message:", error);
          bot.sendMessage(chatId, 'An error occurred while saving your wallet. Please try again.');
        }
      } else {
        bot.sendMessage(chatId, 'The provided address looks invalid. Please ensure it is a valid Ethereum address starting with 0x. If you want to issue a command, please type it directly.');
      }
    }
  });

  console.log('Telegram bot server started and listening for commands...');

  // Listen for /myrewards command
  bot.onText(/\/myrewards/, async (msg) => {
    const chatId = msg.chat.id;
    const userId = msg.from.id;

    try {
      // Ensure user exists, though most flows would have created them
      let user = await dbManager.getUser(userId);
      if (!user) {
        // Optionally create user here if they somehow skipped /start
        // For now, we assume user should exist if they are checking rewards
        bot.sendMessage(chatId, "Please type /start first to initialize your profile.");
        return;
      }

      const totalPoints = await dbManager.calculateUserRewards(userId);
      bot.sendMessage(chatId, `You have accumulated ${totalPoints} reward points so far! Stay tuned for airdrop distribution details.`);
    } catch (error) {
      console.error("Error in /myrewards handler:", error);
      bot.sendMessage(chatId, 'An error occurred while fetching your rewards. Please try again later.');
    }
  });

  // Admin command: /addtask <type> <rewardPoints> <isDailyActive (true/false)> <description>
  bot.onText(/\/addtask (.+?) (\d+) (true|false) (.+)/i, async (msg, match) => {
    const chatId = msg.chat.id;
    const userId = msg.from.id;

    if (!isAdmin(userId)) {
      bot.sendMessage(chatId, "Access Denied. This command is for admins only.");
      return;
    }

    try {
      const type = match[1].toUpperCase();
      const rewardPoints = parseInt(match[2], 10);
      const isDailyActive = match[3].toLowerCase() === 'true';
      const description = match[4];

      if (isNaN(rewardPoints) || rewardPoints <= 0) {
        bot.sendMessage(chatId, "Invalid reward points. Please provide a positive number.");
        return;
      }
      if (!type || !description) {
         bot.sendMessage(chatId, "Invalid format. Usage: /addtask <TYPE> <POINTS> <true|false for daily> <Description>");
         return;
      }

      const customId = `${type}_${Date.now()}`;
      await dbManager.createTask({
        customId,
        type,
        rewardPoints,
        isDailyActive, // Added isDailyActive
        description,
      });
      bot.sendMessage(chatId, `Task added successfully with ID: ${customId} (Daily Active: ${isDailyActive})`);
      console.log(`Admin ${userId} added task: ${customId} - ${description} (Daily: ${isDailyActive})`);
    } catch (error) {
      console.error("Error in /addtask handler:", error);
      bot.sendMessage(chatId, "An error occurred while adding the task. Please check the logs.");
    }
  });

  // Admin command: /settaskdaily <customTaskId>
  bot.onText(/\/settaskdaily ([a-zA-Z0-9_-]+)/, async (msg, match) => {
    const chatId = msg.chat.id;
    const userId = msg.from.id;

    if (!isAdmin(userId)) {
      bot.sendMessage(chatId, "Access Denied. This command is for admins only.");
      return;
    }
    try {
      const customTaskId = match[1];
      if (!customTaskId) {
        bot.sendMessage(chatId, "Usage: /settaskdaily <customTaskId>");
        return;
      }
      const modifiedCount = await dbManager.setTaskDailyStatus(customTaskId, true);
      if (modifiedCount > 0) {
        bot.sendMessage(chatId, `Task ${customTaskId} is now set as a daily task.`);
        console.log(`Admin ${userId} set task ${customTaskId} to daily active.`);
      } else {
        bot.sendMessage(chatId, `Could not find task ${customTaskId} or it was already set to daily.`);
      }
    } catch (error) {
      console.error("Error in /settaskdaily handler:", error);
      bot.sendMessage(chatId, "An error occurred. Please check logs.");
    }
  });

  // Admin command: /unsettaskdaily <customTaskId>
  bot.onText(/\/unsettaskdaily ([a-zA-Z0-9_-]+)/, async (msg, match) => {
    const chatId = msg.chat.id;
    const userId = msg.from.id;

    if (!isAdmin(userId)) {
      bot.sendMessage(chatId, "Access Denied. This command is for admins only.");
      return;
    }
    try {
      const customTaskId = match[1];
      if (!customTaskId) {
        bot.sendMessage(chatId, "Usage: /unsettaskdaily <customTaskId>");
        return;
      }
      const modifiedCount = await dbManager.setTaskDailyStatus(customTaskId, false);
      if (modifiedCount > 0) {
        bot.sendMessage(chatId, `Task ${customTaskId} is no longer a daily task.`);
        console.log(`Admin ${userId} set task ${customTaskId} to daily inactive.`);
      } else {
        bot.sendMessage(chatId, `Could not find task ${customTaskId} or it was already set to non-daily.`);
      }
    } catch (error) {
      console.error("Error in /unsettaskdaily handler:", error);
      bot.sendMessage(chatId, "An error occurred. Please check logs.");
    }
  });

  // Admin command: /removetask <customTaskId>
  bot.onText(/\/removetask ([a-zA-Z0-9_-]+)/, async (msg, match) => {
    const chatId = msg.chat.id;
    const userId = msg.from.id;

    if (!isAdmin(userId)) {
      bot.sendMessage(chatId, "Access Denied. This command is for admins only.");
      return;
    }

    try {
      const customTaskIdToRemove = match[1];
      if (!customTaskIdToRemove) {
        bot.sendMessage(chatId, "Usage: /removetask <customTaskId>");
        return;
      }

      const deletedCount = await dbManager.deleteTask(customTaskIdToRemove);

      if (deletedCount > 0) {
        bot.sendMessage(chatId, `Task "${customTaskIdToRemove}" removed successfully.`);
        console.log(`Admin ${userId} removed task: ${customTaskIdToRemove}`);
      } else {
        bot.sendMessage(chatId, `Task "${customTaskIdToRemove}" not found or could not be removed.`);
      }
    } catch (error) {
      console.error("Error in /removetask handler:", error);
      bot.sendMessage(chatId, "An error occurred while removing the task. Please check the logs.");
    }
  });


})().catch(err => {
  console.error("Failed to start the bot:", err);
  process.exit(1);
});

// Schedule cron job for daily tasks refresh (example)
cron.schedule('0 0 * * *', async () => { // Runs every day at midnight UTC
  console.log('Scheduled daily task refresh: Checking active daily tasks...');
  const dailyTasks = await dbManager.getDailyActiveTasks(); // Example: fetch daily tasks
  console.log(`Found ${dailyTasks.length} daily active tasks.`);
  // Future logic:
  // - Potentially clear completion status for repeatable daily tasks for all users.
  // - Select a new set of random daily tasks if that's the desired logic.
  // - Send a broadcast message to users about new daily tasks.
}, {
  scheduled: true,
  timezone: "UTC"
});
console.log("Daily task refresh job scheduled for midnight UTC.");
