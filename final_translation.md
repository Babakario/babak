**مقدمه:**

این راهنما توضیح می‌دهد که چگونه با استفاده از Cloudflare Workers و فضای ذخیره‌سازی نامحدود تلگرام، یک مرکز آپلود فایل شخصی و رایگان ایجاد کنید.

این سیستم با استفاده از یک Cloudflare Worker به عنوان رابط وب (صفحه آپلود) و پردازشگر کار می‌کند. هنگامی که فایلی را از طریق صفحه وب آپلود می‌کنید، Cloudflare Worker آن را دریافت کرده و مستقیماً از طریق API تلگرام به ربات تلگرام شما ارسال می‌کند. سپس ربات این فایل را به یک چت خاص (که می‌تواند یک کانال یا گروه باشد) ارسال می‌کند. به این ترتیب، شما از فضای ذخیره‌سازی ابری تلگرام به عنوان هاست فایل خود استفاده می‌کنید.

**راهنمای گام به گام ایجاد مرکز آپلود با تلگرام و کلودفلر:**

**مرحله ۱: ایجاد یک ربات تلگرام**
۱. در تلگرام، به ربات @BotFather بروید.
۲. دستور `/newbot` را ارسال کنید.
۳. یک نام برای ربات خود انتخاب کنید (مثلاً My Uploader).
۴. یک نام کاربری برای ربات خود انتخاب کنید که باید به `bot` ختم شود (مثلاً MyPersonalUploader_bot).
۵. پس از ایجاد موفقیت‌آمیز ربات، BotFather یک توکن به شما می‌دهد. چیزی شبیه به `1234567890:ABCdEfGhIjKlMnOpQrStUvWxYz-12345`. این توکن را کپی کرده و در مکانی امن نگهداری کنید.

**مرحله ۲: ایجاد یک Cloudflare Worker**
۱. وارد داشبورد کلودفلر خود شوید.
۲. از منوی سمت چپ، به "Workers & Pages" بروید.
۳. روی "Create application" کلیک کنید و سپس "Create Worker" را انتخاب کنید.
۴. یک نام برای Worker خود انتخاب کنید (مثلاً my-file-uploader) و روی "Deploy" کلیک کنید.
۵. پس از ایجاد Worker، روی "Edit code" کلیک کنید.
۶. تمام کدهای موجود را حذف کرده و آن را با کدی که در Gist ارائه شده است جایگزین کنید (کاربر از قبل این کد را دارد).

**مرحله ۳: مقداردهی اولیه Webhook**
۱. URL مربوط به Worker خود را در یک مرورگر باز کنید.
۲. `/init` را به انتهای URL اضافه کنید. به عنوان مثال، اگر آدرس Worker شما `https://myfiles.be099.workers.dev` است، آدرس `https://myfiles.be099.workers.dev/init` را باز خواهید کرد.
۳. باید پیام "Webhook was set" را مشاهده کنید.

**مرحله ۴: دریافت شناسه چت (Chat ID)**
۱. به ربات تلگرام خود بروید.
۲. دستور `chatid` (یا `/chatid`) را ارسال کنید.
۳. ربات با شناسه چت شما که یک عدد است، پاسخ خواهد داد.
۴. باید این شناسه چت را در کد Cloudflare Worker قرار دهید و جایگزین `<chat-id>` کنید. همچنین باید توکن ربات از مرحله ۱ را در کد قرار دهید و جایگزین `<bot-token>` کنید.

### کد Cloudflare Worker با کامنت‌های فارسی
```javascript
/*
https://github.com/benixal
https://www.youtube.com/@benixal
*/
export default {
// @ts-ignore // این دستور به تایپ‌اسکریپت می‌گوید که خط بعدی را نادیده بگیرد
async fetch(request, env, ctx) {
const botToken = '<bot-token>'; // توکن ربات تلگرام
const chatId = '<chat-id>'; // شناسه چت تلگرام
const url = new URL(request.url); // URL درخواست فعلی
const domain = url.hostname; // دامنه درخواست فعلی
const pathParts = url.pathname.split('/'); // بخش‌های مسیر URL
if (request.method === 'GET' && url.pathname === '/') {
// @ts-ignore // این دستور به تایپ‌اسکریپت می‌گوید که خط بعدی را نادیده بگیرد
const isBotTokenInvalid = !botToken || botToken === '<bot-token>'; // بررسی نامعتبر بودن توکن ربات
// @ts-ignore // این دستور به تایپ‌اسکریپت می‌گوید که خط بعدی را نادیده بگیرد
const isChatIdInvalid = !chatId || chatId === '<chat-id>'; // بررسی نامعتبر بودن شناسه چت
let warningMessage = ''; // پیام هشدار اولیه خالی است
if (isBotTokenInvalid) {
warningMessage += '<p style="color: red;">هشدار: توکن ربات تعریف نشده است</p>';
}
if (isChatIdInvalid) {
warningMessage += '<p style="color: red;">هشدار: شناسه چت تعریف نشده است</p>';
}
const htmlForm = `<!DOCTYPE html>
<html lang="fa">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>آپلود فایل</title>
<style>
* {
margin: 0;
padding: 0;
box-sizing: border-box;
}
body {
background-color: #15181e;
color: white;
font-family: 'Arial', sans-serif;
display: flex;
justify-content: center;
align-items: center;
height: 100vh;
padding: 20px;
}
.container {
background-color: #1f2229;
padding: 40px;
border-radius: 10px;
box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
text-align: center;
}
h1 {
font-size: 2rem;
margin-bottom: 20px;
}
input[type="file"] {
display: block;
margin: 20px auto;
padding: 1rem;
font-size: 1.2rem;
background-color: #2b3038;
color: white;
border: none;
border-radius: 5px;
width: 100%;
max-width: 400px;
cursor: pointer;
}
button {
font-size: 1.5rem;
padding: 1rem 2rem;
margin-top: 20px;
background-color: #4CAF50;
color: white;
border: none;
border-radius: 5px;
cursor: pointer;
transition: background-color 0.3s ease;
}
button:hover {
background-color: #45a049;
}
input[type="file"]:hover {
background-color: #3b4048;
}
</style>
</head>
<body>
<div class="container">
<h1>آپلود فایل</h1>
${warningMessage}
<form action="/upload" method="POST" enctype="multipart/form-data">
<input type="file" name="file" id="fileInput" accept="image/*,video/*" required />
<div id="previewContainer" style="margin: 20px 0; text-align: center;">
<img id="imagePreview" style="max-width: 100%; max-height: 300px; display: none;" />
<video id="videoPreview" controls style="max-width: 100%; max-height: 300px; display: none;"></video>
</div>
<button type="submit">آپلود</button>
</form>
<script>
const fileInput = document.getElementById('fileInput');
const imagePreview = document.getElementById('imagePreview');
const videoPreview = document.getElementById('videoPreview');
const previewContainer = document.getElementById('previewContainer');
fileInput.addEventListener('change', () => {
const file = fileInput.files[0];
if (!file) return;
const fileType = file.type;
const previewURL = URL.createObjectURL(file);
// بازنشانی پیش‌نمایش‌ها
imagePreview.style.display = 'none';
videoPreview.style.display = 'none';
if (fileType.startsWith('image/')) {
imagePreview.src = previewURL;
imagePreview.style.display = 'block';
} else if (fileType.startsWith('video/')) {
videoPreview.src = previewURL;
videoPreview.style.display = 'block';
}
});
</script>
</div>
</body>
</html>
`;
return new Response(htmlForm, {
headers: { 'Content-Type': 'text/html; charset=utf-8' } // تعیین نوع محتوا به همراه UTF-8 برای پشتیبانی از فارسی
});
}
if (request.method === 'GET' && pathParts[1] === 'init') {
const telegramResponse = await postReq("setWebhook", [ // ارسال درخواست برای تنظیم Webhook
{ "url": `https://${domain}/hook` }
]);
const telegramResult = await telegramResponse.text(); // دریافت نتیجه به صورت متن
return new Response(telegramResult);
}
// مدیریت درخواست دانلود فایل
if (pathParts[1] === 'download' && pathParts[2]) {
const fileResponse = await postReq(`getFile`, [ // درخواست اطلاعات فایل از تلگرام
{ "file_id": pathParts[2] }
]);
const fileData = await fileResponse.json(); // تبدیل پاسخ به JSON
const telegramFileResponse = await fetch(`https://api.telegram.org/file/bot${botToken}/${fileData.result.file_path}`); // دریافت فایل از تلگرام
// تغییر هدرهای پاسخ
const newHeaders = new Headers(telegramFileResponse.headers);
// تغییر اختیاری Content-Type اگر 'application/octet-stream' باشد
const contentType = newHeaders.get('Content-Type');
if (contentType === 'application/octet-stream') {
newHeaders.set('Content-Type', ''); // تنظیم یا خالی گذاشتن برای تنظیم خودکار توسط مرورگر
}
newHeaders.delete('Content-Disposition'); // جلوگیری از دانلود اجباری، اجازه نمایش در مرورگر
return new Response(telegramFileResponse.body, { headers: newHeaders });
}
function extractFileIds(obj) { // تابع برای استخراج شناسه‌های فایل از یک شیء
const fileIds = [];
function searchForFileIds(item) { // تابع بازگشتی برای جستجوی شناسه‌های فایل
if (item && typeof item === 'object') {
// بررسی وجود 'file_id' در آیتم
if (item.file_id) fileIds.push(item.file_id);
// جستجوی بازگشتی در تمام خصوصیات شیء
Object.values(item).forEach(searchForFileIds);
} else if (Array.isArray(item)) {
item.forEach(searchForFileIds); // جستجو در آرایه‌ها
}
}
searchForFileIds(obj);
const uniquefileIds = [...new Set(fileIds)]; // حذف شناسه‌های تکراری
return uniquefileIds;
}
async function postReq(url, fields) { // تابع برای ارسال درخواست POST به API تلگرام
const tgFormData = new FormData();
fields.forEach(obj => {
for (let key in obj) {
tgFormData.append(key, obj[key]);
}
});
const telegramResponse = await fetch(`https://api.telegram.org/bot${botToken}/${url}`, {
method: 'POST',
body: tgFormData,
});
return await telegramResponse;
}
if (url.pathname === '/hook' && ['POST', 'PUT'].includes(request.method)) { // اگر درخواست به مسیر /hook و از نوع POST یا PUT باشد
const json = await request.json(); // دریافت اطلاعات درخواست به صورت JSON
const fileIds = extractFileIds(json); // استخراج شناسه‌های فایل از JSON
if (fileIds.length > 0) { // اگر شناسه فایلی وجود داشته باشد
const downloadLinks = await Promise.all( // ایجاد لینک‌های دانلود برای هر شناسه فایل
fileIds.map(async (fid) => {
const fileResponse = await postReq(`getFile`, [ // درخواست اطلاعات فایل
{ "file_id": fid }
]);
const fileData = await fileResponse.json(); // تبدیل پاسخ به JSON
if (fileData.ok) { // اگر درخواست موفقیت‌آمیز بود
return `https://${domain}/download/${fid}/${fileData.result.file_path}`; // بازگرداندن لینک دانلود
} else { // در صورت خطا
await postReq(`sendMessage`, [ // ارسال پیام خطا به کاربر
{ "chat_id": json.message.from.id },
{ "text": "خطا در دریافت اطلاعات فایل" },
{ "parse_mode": "MarkdownV2" },
{ "reply_to_message_id": json.message.message_id }
])
return false; // بازگرداندن false
}
})
);
let msg = [];
for (const item of downloadLinks) { // ایجاد پیام حاوی لینک‌های دانلود
if (item) {
msg.push(`لینک دانلود: \`${item}\``);
}
}
if (msg.length > 0) { // اگر پیامی برای ارسال وجود داشت
await postReq(`sendMessage`, [ // ارسال پیام به کاربر
{ "chat_id": json.message.from.id },
{ "text": msg.join("\n\n") }, // اتصال لینک‌ها با دو خط جدید بین آن‌ها
{ "parse_mode": "MarkdownV2" },
{ "reply_to_message_id": json.message.message_id }
])
}
} else { // اگر شناسه فایلی وجود نداشت (یعنی پیام متنی است)
if ('text' in json.message && json.message.text.toLowerCase().includes('chatid')) { // اگر پیام حاوی 'chatid' بود
await postReq(`sendMessage`, [ // ارسال شناسه چت به کاربر
{ "chat_id": json.message.from.id },
{ "text": `شناسه چت شما: \`${json.message.from.id}\`` },
{ "parse_mode": "MarkdownV2" },
{ "reply_to_message_id": json.message.message_id }
])
} else if ('text' in json.message && json.message.text.includes('/start')) { // اگر پیام /start بود
await postReq(`sendMessage`, [ // ارسال پیام خوشامدگویی
{ "chat_id": json.message.from.id },
{ "text": "خوش آمدید!" },
])
} else { // برای سایر پیام‌های متنی
await postReq(`sendMessage`, [ // درخواست ارسال فایل از کاربر
{ "chat_id": json.message.from.id },
{ "text": "لطفا یک فایل برای من ارسال کنید" },
{ "reply_to_message_id": json.message.message_id }
])
}
}
return new Response(""); // بازگرداندن پاسخ خالی
}
if (url.pathname === '/upload' && request.method === 'POST') { // اگر درخواست به مسیر /upload و از نوع POST بود (آپلود فایل از طریق فرم وب)
const formData = await request.formData(); // دریافت اطلاعات فرم
const file = formData.get('file'); // دریافت فایل از فرم
if (file) { // اگر فایلی وجود داشت
const sendFileToChat = await postReq("sendDocument", [ // ارسال فایل به چت مشخص شده
{ "chat_id": chatId },
{ "document": file }
]);
const sendFileToChatResponse = await sendFileToChat.json(); // تبدیل پاسخ به JSON
if (sendFileToChat.ok) { // اگر ارسال موفقیت‌آمیز بود
const fileIds = extractFileIds(sendFileToChatResponse); // استخراج شناسه‌های فایل
const downloadLinks = await Promise.all( // ایجاد لینک‌های دانلود
fileIds.map(async (fid) => {
const fileResponse = await postReq(`getFile`, [ // درخواست اطلاعات فایل
{ "file_id": fid }
]);
const fileData = await fileResponse.json(); // تبدیل پاسخ به JSON
if (fileData.ok) { // اگر درخواست موفقیت‌آمیز بود
return `https://${domain}/download/${fid}/${fileData.result.file_path}`; // بازگرداندن لینک دانلود
} else { // در صورت خطا
await postReq(`sendMessage`, [ // ارسال پیام خطا به چت
{ "chat_id": chatId },
{ "text": "خطا در ایجاد لینک دانلود" },
{ "parse_mode": "MarkdownV2" }
])
return false; // بازگرداندن false
}
})
);
let msg = [];
for (const itemx of downloadLinks) { // ایجاد پیام حاوی لینک‌های دانلود
if (itemx) {
msg.push(`لینک دانلود: \`${itemx}\``);
}
}
if (msg.length > 0) { // اگر پیامی برای ارسال وجود داشت
await postReq("editMessageCaption", [ // ویرایش کپشن پیام فایل ارسال شده با لینک‌های دانلود
{ "chat_id": chatId },
{ "message_id": sendFileToChatResponse['result']['message_id'] },
{ "parse_mode": "MarkdownV2" },
{ "caption": msg.join("\n\n") } // اتصال لینک‌ها با دو خط جدید بین آن‌ها
])
}
const html = `
<!DOCTYPE html>
<html lang="fa">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>آپلودها</title>
<style>
body {
background-color: #15181e;
}
.container {
display: flex;
flex-direction: column;
gap: 1rem;
padding: 1rem;
}
.item {
display: flex;
flex-direction: column;
text-align: left;
padding: 1rem;
color: white;
border-radius: 8px;
border: 1px solid green;
box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
background-color: white;
}
.link {
color: black;
text-align: left;
padding: 1rem;
letter-spacing: 1px;
font-size: 14px;
}
.dllink {
color: green;
margin: 1rem 1rem 0rem 1rem;
font-weight: bold;
font-size: 1.5rem;
}
.image-preview {
max-width: 100px;
max-height: 100px;
border: 1px solid #ddd;
border-radius: 8px;
}
.image-size {
font-size: 12px;
color: black;
margin-top: 0.5rem;
}
</style>
</head>
<body>
<h1 style="color:#c0b6ff;margin-left:2rem">آپلودهای من</h1>
<div class="container">
${downloadLinks.map(url => {
// بررسی پسوند فایل برای انواع تصویر
const fileExtension = url.split('.').pop().toLowerCase();
const imageExtensions = ['jpg', 'jpeg', 'png', 'webp'];
const isImage = imageExtensions.includes(fileExtension);
// تنظیم تصویر پیش‌نمایش، یا تصویر واقعی یا یک آیکون عمومی
const previewImage = isImage ? url : 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABPCAMAAABs4TM5AAAAAXNSR0IB2cksfwAAAAlwSFlzAAALEwAACxMBAJqcGAAAASxQTFRF/////v7+9vb26Ojo3t7e2dnZ2NjY5ubm9/f3/f392tranJycgICAdnZ2c3NzpKSktbW1t7e3kZGRdHR0dXV1mJiYvb29srKy1NTUy8vLe3t7oqKi1dXVeXl5tLS0+fn5kJCQxcXF09PT+vr6mZmZ6enpenp6xsbGzs7OwsLCzc3NzMzM/Pz8s7OzoKCgk5OTfn5+u7u7o6Ojm5ub7e3tiYmJr6+vf39/7OzsfHx8g4OD0tLS5+fnsbGxx8fH9fX1j4+Pl5eXioqK5OTk7+/v7u7uyMjI4ODgq6urjY2N+Pj4d3d3gYGBfX193Nzc3d3dp6enw8PDi4uLz8/PlZWV8/Pz9PT08vLy0NDQgoKCjIyMpqamhoaG39/flJSU29vbh4eHtra24uLi+/v77g8zIgAAAlNJREFUeJztmM9PE0EUx98zrUxty6VRoJYY0hREjXohGA/KASmJ/4AX+c+8mqhc4dJwaZFowIM/+HERYoLBkAYsEOq2tmOn2N1t9/XNbPbSkH6THnZ3vp+dN327++Yh2MKmgJa8gn/IC7YhwtmVH61zDhAa7O5uzk79fnUF4DBWGDvAQFWNCu93A4yEyqz/AgCi7iU0AaHIAO//D6CiUIBbeKbxtwBEFAowdqrz2wDA6K4HkMbf5gDPHBqADB75AHSuZAOQOrnqB9ARRQMwUeRSyAsAcW2nDTB56BMAonoQDAAithUMACKO3wIBYKi2FQxgr6QhIOl9kkV80wfg5oH33MUcDAEp/EkQVE4aAqAcJU4K/GEMiFwn3kajuGEMAOt2reO1dRhP4AdzgJpFre0wdpSR/gAe9QF9QB/QHcAXKg25P4MEYBxrf1m/wG0OIO/qo2l9UUhAJTmk8xeefmUAcJ8t9tT98ZMzglrESJIHWN9d9Vhv5sFlAFgak7soJgCZ0ijvX5ld5/Kg8lAbTSG7zgECp3IsE9YAdtMfOQBYcob145prcI/mwSUASI3JPZZK5bjgp7P8fJUDyCf67VMizwAqz4o6fyHhBEmEMPNZ8zghnrKpLOfwmAUUS64geyYPTPaNtB5ZOdOdK617+brp3plW9rU03b3TupM37h+Qmq++Me5gUJI3VLHS/AOya7oeCqV6uQzGXRxCU7F3YAO0fSSPZCq8AQ4A4CUu+Umn6fdzb6ENALiwyPTS3AonHuN+zvY5FxDTewaI0IsvD145h/8A56YfXwdUMPEAAAAASUVORK5CYII=';
return `
<div class="item">
<img src="${previewImage}" class="image-preview" alt="پیش‌نمایش فایل" onload="displayImageSize(this)">
<div class="image-size" data-size></div>
<div class="dllink">لینک دانلود:</div>
<div class="link">${url}</div>
</div>`;
}).join('')}
</div>
<script>
function displayImageSize(imgElement) { // تابع برای نمایش اندازه تصویر
if (imgElement.src.startsWith('data:image/png;base64')) return; // اگر تصویر عمومی بود، کاری نکن
const width = imgElement.naturalWidth; // عرض واقعی تصویر
const height = imgElement.naturalHeight; // ارتفاع واقعی تصویر
const sizeElement = imgElement.parentElement.querySelector('[data-size]'); // پیدا کردن عنصر نمایش اندازه
sizeElement.textContent = \`\${width} X \${height}\`; // نمایش اندازه
}
</script>
</body>
</html>
`;
return new Response(html, {
headers: { 'content-type': 'text/html;charset=UTF-8' }, // تعیین نوع محتوا و رمزگذاری برای پشتیبانی از فارسی
});
} else { // اگر ارسال فایل ناموفق بود
return new Response(`ناموفق`, { status: 500 });
}
} else { // اگر فایلی برای آپلود انتخاب نشده بود
return new Response('هیچ فایلی آپلود نشد', { status: 400 });
}
}
}
}
```
