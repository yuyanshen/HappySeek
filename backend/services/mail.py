import smtplib
from email.mime.text import MIMEText
from celery import shared_task

@shared_task
def send_email(to, subject, template):
    msg = MIMEText(template, 'html')
    msg['Subject'] = subject
    msg['From'] = 'noreply@crawler.com'
    msg['To'] = to
    
    with smtplib.SMTP('smtp.exmail.qq.com') as server:
        server.login('user', 'pass')
        server.send_message(msg)

# 任务完成通知示例
def on_task_complete(task_id):
    task = CrawlTask.query.get(task_id)
    user = User.query.get(task.user_id)
    html = f"""
    <h1>您的爬取任务已完成</h1>
    <p>任务ID: {task_id}</p>
    <a href="https://admin.crawler.com/tasks/{task_id}">查看详情</a>
    """
    send_email.delay(user.email, "任务完成通知", html)