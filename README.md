# Reddit Edit Twitter Tipper

A feature missing from Reddit is the ability to get mobile notifications for when another user you are following makes edits to his/her posts. Of course this is expected. Who would want to be notified when a user fixes a spelling error? However, in my situation, there is a user I'm following who is accustomed to updating his followers by appending new thoughts to his latest submitted post. Because his thoughts are critical (stock market related), I would like to be notified in a timely fashion. Also, it would be nice not having to refresh a Reddit page every so often.

Reddit Edit Twitter Tipper is a bot that checks for updates from a specified user and tweets those updates. If the user submits a new post, a link to the new post is tweeted. If he/she makes an update to his/her latest post, the updated text is tweeted. 

While Reddit Edit Twitter Tipper was designed for my unique problem, I hope it can be useful in other scenarios too. Please feel free to learn from it, use it, and/or improve it!

### Dependencies
  - PRAW - Reddit API wrapper for Python
  - Tweepy - Twitter API wrapper for Python

### Usage
  - Replace the constants in the bot.py file with your own Twitter and Reddit API keys and specify the username of the Reddit account to track. Look into environment variables or just hardcode.
  - Schedule the bot.py to be run systematically (i.e. use Crontab on Linux)

### Running on AWS Lambda
###### Note: This is just some self-documentation, but maybe someone will find it useful.
1. Go to https://console.aws.amazon.com/s3/
2. Create bucket
3. Upload empty file named submission_history.txt to the created bucket
4. Go to https://console.aws.amazon.com/lambda/
5. Click **Create function**
6. In the **Function code** section upload a ZIP file
    - This ZIP file not only contains the code, but also all the dependencies (use ```pip install [package] -t .``` in the directory where the code is located). Also, use the **bot_modified_for_aws.py** file.
7. Under **Handler**, change it to **bot_modified_for_aws.main**
8. Configure the **Environment variables** section
9. Scroll up to the **Designer** Section and click **+ Add trigger**
10. Add a **CloudWatch Events**, ensure **Schedule expression** is selected, and for the *cron expression*, use **cron (0/5 \* \* \* ? \*)**. This schedueles the bot script to be run every 5 minutes.
11. In the **Permissions** tab, click on the role name to be taken to another web page.
12. Click **Attach policies** and add **AmazonS3FullAccess**. This will allow access to the S3 submission_history.txt created earlier.
13. Back to the lambda function page, click **Save** and the bot should start.
14. To debug use CloudWatch. There should be a log section somewhere that presents info for each time the script is invoked.

### Todos
* Look into Python logging library and AWS CloudWatch logging
* Tweets have a max character limit of 240, and so I break down the Reddit text to update into chunks. When tweeting a link, make sure not to break the link into different chunks.
* For image links, download images and then attached the image when tweeting instead of sending a URL link.
