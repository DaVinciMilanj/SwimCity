from django.contrib.sitemaps import Sitemap
from pool.models import Pool, Classes


class PoolSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8
    protocol = "https"  # اگر SSL نداری، 'http' بگذار

    def items(self):
        return Pool.objects.all()

    def location(self, obj):
        return f"/api/pools/pool/{obj.id}/"

    def lastmod(self, obj):
        return obj.updated_at  # اگر ندارید، این متد رو حذف کنید


class CourseSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6
    protocol = "https"

    def items(self):
        return Classes.objects.all()

    def location(self, obj):
        return f"/api/pools/pool/{obj.pool.id}/course/"


sitemaps = {
    'pools': PoolSitemap,
    'courses': CourseSitemap,
}
