from django.contrib.sitemaps import Sitemap
from pool.models import Pool, Classes


class PoolSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    protocol = "https"

    def items(self):
        return Pool.objects.filter(status='public')

    def location(self, obj):
        return f"/public-pools/{obj.id}/tickets"


class CourseSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6
    protocol = "https"

    def items(self):
        return Classes.objects.all()

    def location(self, obj):
        return f"/pools/{obj.course_start.pool.id}/course/"


sitemaps = {
    'pools': PoolSitemap,
    'courses': CourseSitemap,
}
