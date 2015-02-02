__author__ = 'Andrey Alekov'

from urllib.parse import urlencode, urlparse
import argparse
import json
import logging
import urllib.request

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %I:%M:%S')
LOG = logging.getLogger()
LOG.level = logging.DEBUG
API_REQ = 'https://api.vk.com/method/{method}?{params}'


def download_photos(hashtag, dest_folder, token, uid):
    downloaded = 0
    token = {'access_token': str(token)}
    params = {'uid': str(uid)}
    params.update(token)
    url = API_REQ.format(method='photos.getAlbums', params=urlencode(params))
    LOG.debug(">> Requested URL: {u}".format(u=url))
    response = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
    LOG.debug("<< JSON data: {d}".format(d=response))
    for a in response['response']:
        LOG.debug("<< Album data: {d}".format(d=a))
        LOG.info("Found album: {name} with {count} photos".format(name=a.get('title'), count=a.get('size')))
        params = {'owner_id': str(uid)}
        params.update(token)
        params.update({'album_id': a.get('aid')})
        url = API_REQ.format(method='photos.get', params=urlencode(params))
        for p in json.loads(urllib.request.urlopen(url).read().decode('utf-8'))['response']:
            LOG.debug("<< Photo data: {d}".format(d=p))
            if p.get('src_xxbig') and (hashtag in p.get('text')):
                LOG.info("Download photo from {u}. Description: {d}".format(u=p.get('src_xxbig'), d=p.get('text')))
                path = dest_folder + urlparse(p.get('src_xxbig')).path.split('/')[-1]
                fh = open(path, "wb")
                fh.write(urllib.request.urlopen(p.get('src_xxbig')).read())
                fh.close()
                downloaded += 1
    LOG.debug("Total downloaded photos: {c}".format(c=downloaded))
    return downloaded


def main():
    p = argparse.ArgumentParser(description='VKPhotos downloader.')
    p.add_argument('-d', dest='dest_folder', default='.', help='Destination folder.')
    p.add_argument('-ht', dest='hashtag', default='#wallpaper', help='Filter by hashtag.')
    p.add_argument('-t', dest='token', help='VK application token.', required=True)
    p.add_argument('-u', dest='uid', help='VK User ID.', required=True)
    args = p.parse_args()
    download_photos(hashtag=args.hashtag, dest_folder=args.dest_folder,
                    token=args.token, uid=args.uid)

if __name__ == "__main__":
    main()