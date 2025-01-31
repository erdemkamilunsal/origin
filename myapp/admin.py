from django.contrib import admin
from .models import ChannelData

class ChannelDataAdmin(admin.ModelAdmin):
    # Hangi alanların listeleneceğini belirliyoruz
    list_display = ('source_category', 'author_name', 'author_nick', 'author_follower_count',
                    'body', 'source', 'link', 'created_time', 'selective_part')

    # Arama kutusu eklemek için
    search_fields = ['source_category', 'author_name', 'author_nick']

    # Filtreleme seçenekleri eklemek için
    list_filter = ('source_category', 'selective_part')

    # Sıralama eklemek için
    ordering = ('-created_time',)

admin.site.register(ChannelData, ChannelDataAdmin)
