from django.db import models


class Task(models.Model):
    """任务模型"""

    STATUS_CHOICES = [
        ("todo", "待办"),
        ("in_progress", "进行中"),
        ("done", "已完成"),
    ]

    PRIORITY_CHOICES = [
        ("low", "低"),
        ("medium", "中"),
        ("high", "高"),
    ]

    title = models.CharField("标题", max_length=200)
    description = models.TextField("描述", blank=True)
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default="todo")
    priority = models.CharField("优先级", max_length=10, choices=PRIORITY_CHOICES, default="medium")
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "任务"
        verbose_name_plural = "任务"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
