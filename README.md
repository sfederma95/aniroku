# Aniroku \(アニ録\)
_Ani\(as in anime\) + Roku \(Japanese word for record\)_  
  
This web application allows users to organize and share their favorite anime/anime movies/and OVA's in one place. Easily sort, label, and rate your favorite titles, and get feedback from other users.  
  
The Aniroku site can be found at: https://aniroku.herokuapp.com/  
  
## Getting started:
* Let's get started by heading to the Homepage!  
  
![Getting started](readme-img/getting-started.png?raw=true)
* For signup let's provide a unique username and e-mail address. I've also included an image address to a cute little anime avatar.  
  
![Signing up](readme-img/signup.png?raw=true)
* Now that we have our portal going, let's make a list  
  
![My portal](readme-img/my-portal.png?raw=true)
![Make a list](readme-img/new-list.png?raw=true)
* This list is pretty incomplete without some anime on it, use the search box to find some! 
   
![Add an anime](readme-img/adding-anime.png?raw=true)
![Search and add](readme-img/add-found-anime.png?raw=true)
* Now let's leave a comment on another user's anime choices  
  
![Leave a comment](readme-img/leave-comment.png?raw=true)
* I've added a few anime with ratings and tags to my "Cute Anime" list, let's see what's been recommended to me...
* Yep, that looks like a good one! Maybe I'll check it out later.  
  
![My recommended page](readme-img/my-recommended.png?raw=true)
## Key features:
* ### Create multiple lists to hold favorite your anime titles:
  * Maybe you want a list for watched/unwatched anime. Maybe you want all your favorite Shojou titles in one place. Maybe you want to show your friends all the cool 90's anime you've watched. Well, you can do all of that. Anime enthusiasts can enjoy the freedom of sorting titles to match their preferences. 
* ### More organization:
  * Further filter within your lists using customized tags. 
  * Simply submit the tag to Aniroku and you \(and any other user\) can use that tag to filter within an anime list. But again, **no profanity!**
* ### Receive and send recommendations between users:
  * Imagine you're looking at AnimeFan123's "Must Watch" list and you see they are clearly missing out on "Shaman King." Aniroku allows you to easily recommend anime to any user directly to the list you're viewing. That way you don't accidently recommend "Shaman King" to their list of "Horror Hits."
* ### Comment on user's anime choices:
  * You can't believe someone would rate "Naruto Shippuden" a 5/10. Easily comment on any anime choices in a socially acceptable and **no profanity** way!
* ### Receive recommendations from the API:
  * As soon as you've rated some titles and added some tags to any of your lists, you will be able to get recommendations from the Jikan API on anime that you might find interesting. 
  * Recommendations are based on keywords from your tags and genres from your top rated anime choices. 
* ### Check out anime based on genre and similar titles:
  * Jikan API also provides recommendations for similar titles to the ones you've clicked on. 
  * For example, clicking on "Cowboy Bebop" will show that you may also be interested in "Samurai Champloo". Sounds about right!
  * You can also click on a genre tag to see which titles fall within the 1 of 43 genres. 
## Resources used:
* Jikan is an unofficial MyAnimeList API. 
* Check out the Jikan API docs at: https://jikan.moe/?ref=apilist.fun
## Technology used:
* Python
* Javascript
* Bootstrap
* CSS
* Flask
* PostgreSQL
### Note:
* To download this project for yourself, please refer to [the instructions file](instructions.md)