from django.db import migrations
from django.utils import timezone
from django.utils.text import slugify


def seed_announcements(apps, schema_editor):
    Announcement = apps.get_model('news', 'Announcement')
    if Announcement.objects.exists():
        return

    sample_data = [
        {
            'title': 'Starwave Live: Solaris Tour Announced',
            'summary': 'We are bringing the Solaris concert experience online with a three-date livestream run.',
            'content': 'Mark your calendars for April 29, May 6, and May 13. Each night features a unique setlist, backstage Q&A, and exclusive merch drops.',
            'category': 'events',
            'tags': ['livestream', 'tour', 'solaristour'],
            'is_pinned': True,
        },
        {
            'title': 'Community Remix Challenge',
            'summary': 'Submit your best reinterpretation of “Neon Afterglow” for a chance to be featured on stream.',
            'content': 'Grab the stems from the resources channel and post your entries by May 20. Winners receive a signed vinyl and Discord flair.',
            'category': 'creative',
            'tags': ['remix', 'contest'],
            'is_pinned': False,
        },
        {
            'title': 'Moderator Applications Open',
            'summary': 'We are expanding the crew with community guides, event hosts, and lore archivists.',
            'content': 'If you love supporting fans, helping organize events, or keeping conversation welcoming, fill out the application form. Interviews begin next week.',
            'category': 'general',
            'tags': ['moderation', 'community'],
            'is_pinned': True,
        },
        {
            'title': 'Synth Lab Sneak Peek',
            'summary': 'A preview of the new sound design tools powering the upcoming EP.',
            'content': 'Watch our producer dive into custom patches, modular rigs, and the AI-assisted sequencer powering the next era of Starwave.',
            'category': 'behind_the_scenes',
            'tags': ['studio', 'preview'],
            'is_pinned': False,
        },
    ]

    now = timezone.now()
    for index, payload in enumerate(sample_data):
        slug = slugify(payload['title'])
        if Announcement.objects.filter(slug=slug).exists():
            slug = f"{slug}-{index}"
        Announcement.objects.create(
            slug=slug,
            published_at=now - timezone.timedelta(days=index),
            **payload,
        )


def remove_announcements(apps, schema_editor):
    Announcement = apps.get_model('news', 'Announcement')
    Announcement.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_announcements, remove_announcements),
    ]
