# Will I Be Late?

A Django Application that answers the simple question on New Yorkers' mind: Will I Be Late? Answer: Probably.

WIBL uses data from the MTA api to show live status updates and upcoming trains for the NYC Subway System. Logged in users can add favorite stations and subway lines for quick access. We cannot control the inconsistent MTA, but we can prepare for potential delays and do our best to get places on time.

## Technologies Used
--- 
Django, Python, JavaScript, jQuery, HTML, CSS, Bootstrap, PostgreSQL, bit.io

[MTA api](https://api.mta.info/#/landing)

*Jon Thorton's* [MTA Realtime API JSON Proxy](https://github.com/jonthornton/MTAPI)

## Screenshots
---
![Home Page](https://i.imgur.com/IdH9yba.png)

![FavStations](https://i.imgur.com/v7LKwwX.png)

![FavSubways](https://i.imgur.com/CqCM8bg.png)


## Getting Started
---
[Click Here](http://willibelate.herokuapp.com/) to see the deployed app.  

- Search for specific train stations
- Browse subway lines
- View real time upcoming trains and status alerts
- Sign up to add favorite lines or stations

## Future Enhancements
---
- Edit Stations file to differentiate between stations with the same name (ie: 125 St --> 125 St (A,B,C,D))
- Use location data to show users their five closest stations
- Add animations to show approaching trains on a timeline
- Allow users to comment on train lines or stations to share live updates with the user community. Posts would timeout after 3 hours to keep information current and relevant.