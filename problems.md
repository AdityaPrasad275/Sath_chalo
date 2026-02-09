what i do know/currently built in backend

(1) ingest gtfs data into "stops" , "routes" and "trips"
(2) each stop got lat lon, name but no "direction", is it on this side of road or that side
(3) we got routes . ok so we havent got a view that shows the stops in a route (or the shape of that route)
(4) we got trips , we got list of stops on that trip, time, loc. we also added a "headed_to" to be the last stop on the trip
(5) that was the whole gtfs data
(6) upcoming trips on a stop `api/gtfs/stops/S001/upcoming/`
are for i think 1 hr. no acttualy `        # Calculate window: 15 mins ago to 2 hours from now`
(7) the time in our actual data is in actually utc instead of being in asia/kolkata whatever. 


Now questions ->
(1) this was built on synthetically generated gtfs data [from this script](/home/ap/Personal_Files/coding/gt/data_tools/gtfs_generator/gtfs_generator.py)

How do we make sure new gtfs data, like bmtc, mumbai wahtever can also be ingested into our system, what are the properities we are looking after (sort of the contract with gtfs data)
(2) for the stop direction, my idea was figure out all routes going from this stop, and the direction then becomes like the common demoniator stop or the most common denominaotr, sort of a "distance to the stop" + "commmon for how many routes going through this stop". This can help us distinguish between two sides of a raod, because it is quite prossbile that stops might have same name , different id, corersponding to different side of road, and hence we need a "toward"

(3) what is "shape_id" field in trips. how are we populating it, currently its empty, what is supposed to be

(4) simple showing gtfs data is great but we need the confidence/user feedback layer and i am literally not sure how to do that. see basically the evidence/ 

```
class Observation(models.Model):
    class ObservationType(models.TextChoices):
        WAITING_AT_STOP = 'WAITING', 'Waiting at Stop'
        ON_BUS = 'ON_BUS', 'On Bus'
        BUS_PASSED = 'PASSED', 'Bus Passed'

    user_id = models.CharField(max_length=255) # Anonymous session ID or user ID
    timestamp = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=20, choices=ObservationType.choices)
    stop = models.ForeignKey(Stop, on_delete=models.SET_NULL, null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.type} by {self.user_id} at {self.timestamp}"

```

is currently this. is this all? appropriate? i belive the observation type is currently a bit small. like let me think what all can a user feedback ->
(1) the bus is showing schudled but has not come . can be late +1 min or can be late +15 min. but genrrally a user will not really wait? 15 mins? so its sort of a we only get the "bus has not come" for some max waiting duration
(2) the bus just left in front of my eyes, even though its showing 5 min waiting -> well it could be the previous bus has come later? yeah idk this observation doesnt make sense because like there are trips right. so it is possible for the bus you're seeing to be an earlier trip or be this trip came early
(3) the bus didnt stop at this stop. 
(4) for the the bus showing schudeled time but has not come, when do we go from it is late vs it is not coming
(5) and this sitatuion happend irl, the bus we were on, got some parts jammed or somethign and hence was stuck there in the middle of the road, so to all the people in later sotps, how do we communicate that? because then what happened is we changed buses. we changed destination and rerouted.  so sort of a user movement needs to be peroeply carectorised into like one of the trips
(6) the bus took a different route. it was supposed to go here it went there. 

See i am stuck in actually a sort of fork between two thigns. you got realtime events like bus stopped ebcause some part bad. or it rerouted. right how do you communicate that to the users. 

then we got systemic errros. this bus is awlays +1 min late or something. this is sort of a aggregate oever multiple user feedbacks. and it sort of a "is correct ~90% time" (huge number huge deeam lmao). whcih qeusiton do we answer. how do we cater our backend to answer that quesiton. currently the way evidence/ and realtime/ is setup, i beleiv its answering the aggragtae one. but i am not sure if we are taking good anough data from users to make sense

and hoenstly the first one, the realtime thing, bus stooped, bus rerouted, the bus is exactly here at this poitn in time, is for me a more exciting quesiton and ofc a much more probelmatic one. 