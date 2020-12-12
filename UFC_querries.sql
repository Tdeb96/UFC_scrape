/* Let's run some querries*/

#Amount of athletes per country
select count(Name), Nation
from athletes
group by Nation
order by count(Name) desc;

#Athletes with the most amount of career wins, top 10
select Name, Wins, Losses, Draws, Division
from athletes
order by wins desc
limit 10;

#Who is the knockout artist of the heavyweight division
select Name, Win_by_way_KO_TKO, Wins, Losses, Draws, Division
from athletes
where Division = "Heavyweight Division"
order by Win_by_way_KO_TKO desc
limit 10;

#top 10 biggest ape indexes (Height/reach) in current fighters for fighters taller than 180
select Name, Height, Weight, Reach, Division, Reach/Height as Ape_index
from athletes
where Division <> "Former Fighter" and height > 180
order by Ape_index desc
limit 10; 

#Top 10 guys with the most significant head strikes in the heavyweight division 
select Name, Height, Weight, Reach, Division, Sig_strikes_head
from athletes
where Division = "Heavyweight Division"
order by Sig_strikes_head desc
limit 10; 

#UFC wins for "Donald Cerrone"
#First I did not create a winner_name variable, so had to do it using this obscure code
with blue_wins as (
select count(fights.Fighter_ID_blue) as wins_blue, fights.Fighter_ID_blue as ID_blue
from athletes 
left join fights
on athletes.Fighter_ID = fights.Fighter_ID_blue
where fights.Winner = "Blue"
group by fights.Fighter_ID_blue
),
#wins in the red corner
red_wins as (
select count(fights.Fighter_ID_red) as wins_red, fights.Fighter_ID_red as ID_red
from athletes 
left join fights
on athletes.Fighter_ID = fights.Fighter_ID_red
where fights.Winner = "Red"
group by fights.Fighter_ID_red
),
wins as (
select (blue_wins.wins_blue + red_wins.wins_red) as wins_UFC, blue_wins.ID_blue as ID_wins
from blue_wins
join red_wins
on blue_wins.ID_blue = red_wins.ID_red)

select athletes.Name as Name, wins.wins_UFC as UFC_wins
from athletes
left join wins
on athletes.Fighter_ID = wins.ID_wins
where athletes.Name = "Donald Cerrone"
order by wins.wins_UFC desc;

#Now I can find the total wins in the UFC much easier using the Winner_name 
select athletes.Name, count(athletes.Name) as UFC_wins
from athletes
left join fights
on athletes.Name = fights.Winner_name
where athletes.Name = "Donald Cerrone"
group by athletes.Name;

#Find the top 10 most knockouts in the UFC
select athletes.Name, count(athletes.Name) as Knockouts
from athletes
left join fights
on athletes.Name = fights.Winner_name
where fights.Finish_method = "KO/TKO"
group by athletes.Name
order by Knockouts desc
limit 10;