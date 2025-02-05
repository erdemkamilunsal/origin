from django.contrib import admin
from .models import ChannelData, LatestDataTable


class ChannelDataAdmin(admin.ModelAdmin):
    list_display = ('source_category', 'source', 'link', 'created_time', 'selective_part')
    search_fields = ['source_category', 'author_name', 'author_nick']
    list_filter = ('source_category', 'selective_part')
    ordering = ('-created_time',)


class LatestDataTableAdmin(admin.ModelAdmin):
    # Görüntülenecek alanlar
    list_display = ('source_category', 'selective_part', 'source', 'created_time', 'author', 'total')

    # Arama yapılacak alanlar
    search_fields = ['source_category', 'source', 'selective_part', 'author']

    # Filtreleme yapılacak alanlar
    list_filter = ('source_category', 'selective_part', 'source')

    # Varsayılan sıralama
    ordering = ('-created_time',)


# Admin paneline model ekleme
admin.site.register(ChannelData, ChannelDataAdmin)
admin.site.register(LatestDataTable, LatestDataTableAdmin)
