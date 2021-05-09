# Python-Instagram-API

aims to bring API-like features (rich and intensive functions then official API) of instagram into python

## Getting Started

these instructions will get you a copy of the project up and running on your local machine

### Requirements

Python3
Requests

### Import

simply get a copy of instagram.py from repo and move it to your project directory and import it

### Examples

#### Creating Login Instance

```python
import instagram  # importing file

insta = instagram.Instagram() # create an instance
res = insta.login(username='your username', password='your password') #perform login. it will give out login info of user logged in like userID and auth.

## if above operation yields auth != True then you can read res in order to understand errors

if not insta.isAuth: ## checks if above login was successful or not same as res.text['Authentication']
	print('Failed to login in')
else:
	print('login successful')
```

#### fetch any user data on instagram

after creating Instagram instance (insta) 

NOTE :: login is not always necessary by default logged in as guest and can fetch open profiles as well as private user's profile picture but controlling like features are not available

you can get anyone's instance over intagram by
```
insta.{username}
```

like

```python
nike = insta.nike
google = insta.google
```

#### User Operation

there are various operation that you can do over users instance, like, gettting there basic info like fullname/business mail/phone/external url and many more that you can explore by typing {user_instance}. on your ide or code editor that have code completion

special opertations are also there like, getting all stories/post/highlights of the user 
all of the sp operation have 2 versions :
	1 :: that yields direct link of photo or video
	2 :: that gives source dictionary through which links are extracted. they can be pretty useful as they are the same dict codes that insta provides on website 

getting source extends users capablity as they can play and code better and fesiable things (like they yield date and time stamp in iso format)

```python
import instagram

insta = instagram.Instagram()
insta.login('ussername', 'password')

if not insta.isAuth: print('login failed')

nike = insta.nike

src = nike.story('Source') # get src in dictionary format for story

## or ##

for i in nike.story('iterlink'): iterlink generates a python generator object
	print(i)  ## or download the picture or video with link
```

same goes to other sp ops

#### Logged in User Functions

you can get a full story tray that you have seen in instagram's top bar by main_instance.storytray()

```python
tray = insta.storytray() # give storytray line wise in list format
firstelement = tray['tray'][0]
print(firstelement['items']) #these are the items in story 

# to get whose story it is
print(firstelement['user']) # printoff user details
```
