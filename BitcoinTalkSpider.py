import scrapy
import pandas as pd

class BitcoinTalkSpider(scrapy.Spider):
    name = "bitcointalk"
    start_urls = ["https://bitcointalk.org/index.php?board=1.0"]

    def __init__(self):
        super().__init__()
        self.df = pd.DataFrame(columns=['Subject', 'Started by', 'Replies', 'Views', 'Last post'])

    def parse(self, response):
        # find table element containing post data
        table_element = response.css('table.bordercolor')

        # find all rows in table
        rows = table_element.css('tr')

        # loop through rows and extract data for each post
        for row in rows:
            # skip header row
            if row.css('::attr(class)').get() == 'titlebg':
                continue

            # extract data from columns
            subject_element = row.css('td:nth-child(3) span.subject a')
            started_by_element = row.css('td:nth-child(4) a')
            replies_element = row.css('td:nth-child(5)')
            views_element = row.css('td:nth-child(6)')
            last_post_element = row.css('td:nth-child(7) span small')

            subject = subject_element.css('::text').get()
            started_by = started_by_element.css('::text').get()
            replies = replies_element.css('::text').get()
            views = views_element.css('::text').get()
            last_post = last_post_element.css('::text').get()

            # add data to item
            yield {
                'Subject': subject,
                'Started by': started_by,
                'Replies': replies,
                'Views': views,
                'Last post': last_post
            }

            # add data to dataframe
            data = {'Subject': subject, 'Started by': started_by, 'Replies': replies, 'Views': views, 'Last post': last_post}
            self.df = self.df.append(data, ignore_index=True)

        # check if there is a next page
        next_button = response.css('div.pagesection span.next a')
        if 'disabled' not in next_button.css('::attr(class)').get():
            # navigate to next page
            next_page = next_button.css('::attr(href)').get()
            yield response.follow(next_page, self.parse)

    def closed(self, reason):
        # save dataframe to csv file
        self.df.to_csv('bitcointalk.csv', index=False)
