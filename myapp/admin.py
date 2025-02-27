from django.contrib import admin
from .models import LatestData, ScraperLog, Latest7Days, MostSharedContent  # Modelleri import ediyoruz


class LatestDataAdmin(admin.ModelAdmin):
    # Görüntülenecek alanlar
    list_display = ('source_category', 'author_name', 'author_nick', 'source', 'created_time', 'selective_part')

    # Arama yapılacak alanlar
    search_fields = ['source_category', 'author_name', 'author_nick', 'source']

    # Filtreleme yapılacak alanlar
    list_filter = ('source_category', 'selective_part', 'source')

    # Varsayılan sıralama
    ordering = ('-created_time',)


class ScraperLogAdmin(admin.ModelAdmin):
    # Görüntülenecek alanlar
    list_display = ('last_update',)

    # Varsayılan sıralama
    ordering = ('-last_update',)


class Latest7DaysAdmin(admin.ModelAdmin):
    # Görüntülenecek alanlar
    list_display = ('source_category', 'selective_part', 'source', 'created_time', 'author', 'total')

    # Arama yapılacak alanlar
    search_fields = ['source_category', 'source', 'selective_part', 'author']

    # Filtreleme yapılacak alanlar
    list_filter = ('source_category', 'selective_part', 'source')

    # Varsayılan sıralama
    ordering = ('-created_time',)


class MostSharedContentAdmin(admin.ModelAdmin):
    list_display = ('name', 'source_category', 'selective_part', 'source', 'created_time')
    list_filter = ('source_category', 'selective_part', 'source', 'created_time')  # Filtreleme alanları
    search_fields = ('name', 'content')  # Arama alanları

# Admin paneline modelleri ekleme
admin.site.register(LatestData, LatestDataAdmin)
admin.site.register(ScraperLog, ScraperLogAdmin)
admin.site.register(Latest7Days, Latest7DaysAdmin)
admin.site.register(MostSharedContent, MostSharedContentAdmin)