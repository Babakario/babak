// telegram_bot_project/database.js
const { MongoClient } = require('mongodb');
require('dotenv').config(); // Ensure .env is loaded for MONGODB_URI

const MONGODB_URI = process.env.MONGODB_URI;

let db;
let usersCollection;
let tasksCollection;

async function connectDB() {
  if (db) return db; // Return existing connection if already connected
  if (!MONGODB_URI) {
    console.error('MONGODB_URI not found in .env file. Please ensure it is set.');
    process.exit(1); // Exit if DB URI is not set
  }
  try {
    const client = new MongoClient(MONGODB_URI);
    await client.connect();
    const databaseName = MONGODB_URI.split('/').pop().split('?')[0]; // Extract DB name from URI
    db = client.db(databaseName);
    usersCollection = db.collection('users');
    tasksCollection = db.collection('tasks');
    console.log(`Successfully connected to MongoDB database: ${databaseName}`);
    return db;
  } catch (error) {
    console.error('Could not connect to MongoDB:', error);
    process.exit(1); // Exit if connection fails
  }
}

async function getUser(telegramId) {
  if (!usersCollection) await connectDB();
  return usersCollection.findOne({ telegramId: parseInt(telegramId) });
}

async function createUser(telegramId) {
  if (!usersCollection) await connectDB();
  const newUser = {
    telegramId: parseInt(telegramId),
    walletAddress: null,
    completedTaskIds: [],
    points: 0, // Initialize points
  };
  await usersCollection.insertOne(newUser);
  return newUser;
}

async function updateUserWallet(telegramId, walletAddress) {
  if (!usersCollection) await connectDB();
  return usersCollection.updateOne({ telegramId: parseInt(telegramId) }, { $set: { walletAddress } });
}

async function completeTaskForUser(telegramId, customTaskId) {
  if (!usersCollection) await connectDB();
  // First, ensure the user exists
  let user = await getUser(telegramId);
  if (!user) {
    user = await createUser(telegramId);
  }
  return usersCollection.updateOne({ telegramId: parseInt(telegramId) }, { $addToSet: { completedTaskIds: customTaskId } });
}

async function getUserCompletedTasks(telegramId) {
  if (!usersCollection) await connectDB();
  const user = await usersCollection.findOne({ telegramId: parseInt(telegramId) });
  return user ? user.completedTaskIds : [];
}

async function getTask(customId) {
  if (!tasksCollection) await connectDB();
  return tasksCollection.findOne({ customId });
}

async function getAllTasks() {
  if (!tasksCollection) await connectDB();
  return tasksCollection.find({}).toArray();
}

async function createTask(taskData) {
  if (!tasksCollection) await connectDB();
  // taskData should include customId, description, type, rewardPoints, isDailyActive
  const taskToInsert = { ...taskData };
  if (taskToInsert.isDailyActive === undefined) {
    taskToInsert.isDailyActive = false; // Default to false if not provided
  }
  const result = await tasksCollection.insertOne(taskToInsert);
  return result;
}

async function initializeDefaultTasks() {
  if (!tasksCollection) await connectDB();
  const defaultTasks = [
    { customId: 'TELEGRAM_JOIN_1', description: "Join our Telegram Channel", type: 'TELEGRAM_JOIN', rewardPoints: 10, link: "YOUR_TELEGRAM_CHANNEL_LINK", isDailyActive: true },
    { customId: 'TWITTER_FOLLOW_1', description: "Follow us on Twitter", type: 'TWITTER_FOLLOW', rewardPoints: 10, link: "YOUR_TWITTER_PROFILE_LINK", isDailyActive: true },
    { customId: 'WALLET_CONNECT_1', description: "Connect your Web3 Wallet", type: 'WALLET_CONNECT', rewardPoints: 5, isDailyActive: false },
    { customId: 'READ_DOCS_1', description: "Read our documentation", type: 'GENERAL', rewardPoints: 3, isDailyActive: false },
    // Add more tasks as needed
  ];

  for (const task of defaultTasks) {
    const existingTask = await getTask(task.customId);
    if (!existingTask) {
      await createTask(task);
      console.log(`Created default task: ${task.description}`);
    }
  }
}

module.exports = {
  connectDB,
  getUser,
  createUser,
  updateUserWallet,
  completeTaskForUser,
  getUserCompletedTasks,
  getTask,
  getAllTasks,
  createTask,
  initializeDefaultTasks,
  // For potential direct use if needed, though collections are not directly used by index.js
  // getUsersCollection: () => usersCollection,
  // getTasksCollection: () => tasksCollection,
  calculateUserRewards,
  deleteTask,
  getDailyActiveTasks,
  setTaskDailyStatus,
};

async function getDailyActiveTasks() {
  if (!tasksCollection) await connectDB();
  return tasksCollection.find({ isDailyActive: true }).toArray();
}

async function setTaskDailyStatus(customTaskId, isActive) {
  if (!tasksCollection) await connectDB();
  const result = await tasksCollection.updateOne(
    { customId: customTaskId },
    { $set: { isDailyActive: isActive } }
  );
  return result.modifiedCount;
}

async function deleteTask(customTaskId) {
  if (!tasksCollection) await connectDB();
  const result = await tasksCollection.deleteOne({ customId: customTaskId });
  return result.deletedCount;
}

async function calculateUserRewards(telegramId) {
  if (!usersCollection || !tasksCollection) await connectDB();

  const user = await getUser(parseInt(telegramId));
  if (!user || !user.completedTaskIds || user.completedTaskIds.length === 0) {
    return 0;
  }

  try {
    const taskPromises = user.completedTaskIds.map(customTaskId => getTask(customTaskId));
    const completedTasksObjects = await Promise.all(taskPromises);

    let totalPoints = 0;
    for (const task of completedTasksObjects) {
      if (task && task.rewardPoints) {
        totalPoints += task.rewardPoints;
      }
    }
    return totalPoints;
  } catch (error) {
    console.error(`Error calculating rewards for user ${telegramId}:`, error);
    return 0; // Return 0 in case of error
  }
}
