from django.contrib.sitemaps import Sitemap
from pool.models import Pool, CreateClass, Classes


class PoolSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Pool.objects.all()

    def lastmod(self, obj):
        return obj.updated_at  # فرض بر این است که فیلدی برای تاریخ به روز رسانی دارید


class CourseSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Classes.objects.all()


sitemaps = {
    'pools': PoolSitemap,
    'courses': CourseSitemap,
}
