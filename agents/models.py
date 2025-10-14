import re
import itertools
from django.db import models
from django.utils.text import slugify as django_slugify
class Agent(models.Model):
    display_id = models.CharField(max_length=50, blank=True)
    type_label = models.CharField(max_length=200, blank=True)
    site_text = models.TextField(blank=True)          
    phone_display = models.CharField(max_length=200, blank=True)
    complain_text = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.display_id}-{self.phone_display}")[:200] 
            slug = base
            for i in itertools.count(1):
                if not Agent.objects.filter(slug=slug).exists():
                    break
                slug = f"{base}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.display_id} - {self.type_label}"


class GlobalWhatsApp(models.Model):
    numbers = models.TextField(help_text="Add multiple WhatsApp numbers, one per line")

    def get_numbers_list(self):
        return [num.strip() for num in self.numbers.splitlines() if num.strip()]

    def __str__(self):
        return "Global WhatsApp Numbers"



def unicode_slugify(value):
    """
    Create a slug that allows Bangla + Latin letters + digits + dash/underscore.
    Uses Unicode block for Bengali: \u0980-\u09FF
    """
    value = str(value).strip()
    # replace spaces with dash
    value = re.sub(r'\s+', '-', value)
    # remove any character that is NOT: word char, dash, Bengali letters, Bengali digits
    value = re.sub(r'[^\w\-\u0980-\u09FF\u0966-\u096F]+', '', value, flags=re.U)
    return value.lower()

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = unicode_slugify(self.name) or django_slugify(self.name)
            slug = base_slug
            for i in itertools.count(1):
                if not Category.objects.filter(slug=slug).exists():
                    break
                slug = f"{base_slug}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = unicode_slugify(self.title) or django_slugify(self.title)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

