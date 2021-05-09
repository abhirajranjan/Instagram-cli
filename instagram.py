import requests, json, pickle, os
from collections import namedtuple


class UserProfile:
        def __init__(self, dict):
                self.__dict__.update(dict)
                self.__protdict__ = self.__dict__
                userProfile = self.__inst__.getJsonByUsername(self.username)
                try:
                        self.__protdict__.update(userProfile['entry_data']['ProfilePage'][0]['graphql']['user'])
                except Exception:
                        return '\'{0}\' Not Found'.format(self.username)

        def __getitem__(self, item):
                if item in self.__dict__:
                        return self.__dict__[item]
                elif item in self.__protdict__:
                        return self.__protdict__[item]
                else:
                        raise KeyError

        def __repr__(self):
                try:
                        username = self['username']
                except KeyError:
                        username=''
                return 'userProfile( username=\'{0}\' )'.format(username)\
                       if username else 'userProfile()'

        def __getattr__(self, attr):
                if attr in ['story', 'posts']:
                        return getattr(self, attr)                        
                return self[attr]
        
        def story(self, args=['Source', 'iterlink']):
                if args not in ['Source', 'iterlink']: return
                if args == 'Source':
                        return self.__inst__.getStoryDataByUserName(self.username)['reels_media'][0]['items']
                return self.__inst__.getStoryByUserName(self.username)

        @property
        def posts(self):
                pass

        @posts.getter
        def posts(self):
                return self['__inst__'].session.getpost(self['username'])


class Instagram:
        session        = requests.Session()
        ## session in login is just for backup session
        url            = namedtuple('URL', ['base', 'login', 'ofuserstory', 'story'])
        _login          = namedtuple('_login', ['isAuth', 'username', 'password', 'userData'])
        cache          = namedtuple('cache', ['story'])

        # user-agent
        UA             = 'Mozilla/5.0 (X11; Linux i686; rv:89.0) Gecko/20100101 Firefox/89.0'

        #insta compaitable UA
        _InstaUA        = 'Instagram 123.0.0.21.114 ' + UA[UA.find('('):]

        # urls
        url.base       = 'https://www.instagram.com/'
        url._login      = url.base + 'accounts/login/ajax/'
        url.story      = 'https://i.instagram.com/api/v1/feed/reels_media/?reel_ids={0}'
        url.storytray  = 'https://i.instagram.com/api/v1/feed/reels_tray/'

        #init login details
        _login.isAuth   = False
        _login.username = _login.password = _login.userData = ''

        #init
        cache.story    = False

        def __init__(self, *args, **kwargs):
                self.session.headers            = {'user-agent': self._InstaUA}
                self.session.cookies['ig_pr']   = '1'
                self.session.headers['Referer'] =  self.url.base

                if os.path.lexists(os.path.join(os.path.dirname(__file__), 'CacheData.cc')):
                        try:
                                with open(os.path.join(os.path.dirname(__file__), 'CacheData.cc'), 'rb') as file:
                                        data = pickle.load(file)
                                self._login.username = data['username']
                                self._login.password = data['password']
                                self.session        = data['session']
                                self._login.userData = data['userData']
                                self._login.isAuth   = True
                        except EOFError:
                                pass

                if 'username' and 'password' in kwargs:
                        print(self.login(username=args['username'], password=args['password']))
                elif len(args) == 2:
                        print(self.login(username=args[0], password=args[1]))

        @property
        def isAuth(self):
                pass
        
        @isAuth.getter
        def isAuth(self):
                return self._login.isAuth

        @property
        def username(self):
                pass

        @username.getter
        def username(self):
                return self._login.username

        def login(self, username, password):
                req = self.session.get(self.url.base)

                self.session.headers['X-CSRFToken'] = req.cookies['csrftoken']

                req = self.session.post(self.url._login, data={
                        'username': username,
                        'password': password},
                                             allow_redirects = True)

                self.session.headers['X-CSRFToken'] = req.cookies['csrftoken']
                jsonify = json.loads(req.text)

                if jsonify.get('authenticated'):
                        self.session.headers.update({'user-agent': self.UA})
                        self.session.headers.update({'X-IG-App-ID':'936619743392459',
                                         'X-IG-WWW-Claim': 'hmac.AR3SysXdrWAKuxLEoedUb6x3nDdoA6pyKVbr7Hf0CtZi4u9U',
                                                'Origin' : 'https://www.instagram.com',
                                                    'DNT': '1',
                                               'Alt-Used': 'i.instagram.com',
                                                'Referer': 'https://www.instagram.com/'})
                        self._login.isAuth = True
                        self._login.username = username
                        self._login.password = password
                        self._login.userData = jsonify

                        with open(os.path.join(os.path.dirname(__file__), 'CacheData.cc'), 'wb') as file:
                                pickle.dump({'username':self._login.username,
                                             'password':self._login.password,
                                             'session':self.session,
                                             'userData':self._login.userData,
                                             }, file)

                return jsonify

        @property
        def story(self):
                pass

        @story.getter
        def story(self):
                ## GET self.url.story.format(['id'])
                ## will give speific user story data
                return self.fetch('getStoryByUserName') if self.cache.story else self.fetch('storytray')

        @story.setter
        def story(self, object):
                self.cache.story = object
                

        def getJsonByUsername(self, username):
                userdata = self.session.get(self.url.base + username)
                user = json.loads(userdata.text.split('window._sharedData =')[1].split(';</script>')[0])
                if user:
                      return user
                return

        def fetch(self, item: ['storytray', 'storybyusername']):
                _type = type(item)
                if _type == str:
                        return self.__getattribute__(item)()

        def storytray(self):
                return json.loads(self.session.get(self.url.storytray).text)

        def getStoryDataByUserName(self, username=''):
                user = self._getUser(self.getJsonByUsername(username))
                ## returning data['reels'][{id}]['items'][0]['video_versions'][0]['url']
                ## this gives video formats of video type stories
                return json.loads(self.session.get(self.url.story.format(user['id'])).text)

        def getStoryByUserName(self, username=''):
                if username:
                        slides = self.getStoryDataByUserName(username)
                elif self.cache.story:
                        slides = self.getStoryDataByUserName(self.cache.story)
                else:
                        SyntaxError('getStoryByUserName called without any args')

                for item in slides['reels_media'][0]['items']:
                        yield item['image_versions2']['candidates'][0]['url']
                        if 'video_versions' in item:
                                yield item['video_versions'][0]['url']

                self.cache.story = False

        def _getUser(self, json):
                return json['entry_data']['ProfilePage'][0]['graphql']['user']

        def iterUserPostBy(self, kwarg: ['username']):
                if (self.isAuth) and ('username' in kwarg):
                        user = self.getJsonByUsername(kwarg['username'])
                        if user:
                                for ind, _ in enumerate(user['edge_owner_to_timeline_media']['edges']):
                                        node  = _[ind]['node']
                                        if node['__typename'] == 'GraphSidecar':
                                                posts = node['edge_sidecar_to_children']['edges']
                                                for i , post in enumerate(posts):
                                                        if (post[i]['node']['__typename'] == 'GraphImage') and not (post[i]['node']['is_video']):
                                                                self._download(post[i]['node']['display_url'])
        def __getattr__(self, username):
                profile =  UserProfile({'username':username, '__inst__':self})
                return profile
