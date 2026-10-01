---
type: project
last_accessed: 2026-09-29
relevance: 0.97
tier: active
---
Now, this is, in my opinion, a good
sign. I'm glad to see that we have 80%
of our portfolio is actually actively in
a position now. Now, unfortunately,
we're not looking too good. Today was
not a good day. We have lost about
and we ran into a bit of a hiccup. So,
it's definitely nothing crazy at all,
but we are up a little bit. Look how
much we've gone up.
So, I'm going to give Codex $10,000 of
real money to trade stocks for me. I
actually did this experiment before
using Open Claw, and it went all right,
but there was one rule that I'm going to
break in this challenge. And that rule
was that once I set the system up, I
couldn't touch it. But this time, the
rules will be different because every
day, I can make up to two changes if I
want to. And even if I lose all my
money, I can't stop it from trading.
Now, the final results will be compared
to the S&amp;P 500, and I have to beat it to
win. But if I can't beat it, I'll be
giving away a free VIP ticket to our
upcoming event, October 17th and 18th,
to one of you guys. So, those are the
rules, and let's see what happens.
All right, guys. So, it's technically
day zero because the market is closed
today. Tomorrow is when the challenge
officially kicks off, and that is
official day one. But what I did today
is I just got everything set up. So, let
me show you real quick what the strategy
is. So, I actually started off by
wanting to just get its advice. I said,
"Hey, I'm going to be doing this trading
challenge. We're going to start with
$10,000. We have seven trading days to
make as much money as possible. So, I
want you to do a ton of research and
help me figure out what we need to do."
So, it delegated out to a ton of
different trading agents, and they did
research, and they basically helped me
create a strategy. And now, let me show
you where we're at. So, we got to this
place now where we're going to have six
wake-ups as far as actions that are
being taken, and then we're going to
have two different actions for
notifications, which I'll explain in a
sec. We'll have one before the market
opens to read news, to check the
account, and choose what stocks to
watch. We'll have another one about an
hour in to look for the first qualifying
trade. We'll have one midday to review
positions and consider the last new
trade. We'll have one in the afternoon
to manage the existing positions.
&gt;&gt; [music]
&gt;&gt; One at 2:15 to close remaining
positions, and then one right before
market close to confirm whether we're
out and record [music] the day's
results. Now, what's really important to
think about here is the continuity
because we want every single agent to
wake up and to not feel completely
stateless or [music] useless. So, every
time an agent wakes up, it's going to
leave some sort of handoff message, and
then the next agent, when it wakes up,
will read that message and then take
action and then leave the next agent
another handoff message. So, this is
going to very much feel like we just
have one [music] agent working through
the whole thing. And so, what that
actually looks like in practice is all
of the routines are set up and they look
like they're deactivated because they
don't become active until tomorrow
because, you [music] know, today is not
a trading day. Anyways, we'll have this
one at 7:45, we'll have this one at
9:30, 11:00 a.m., 1:00 p.m., 2:15, 2:45,
and 3:15. And what's really cool about
all these routines is that they all run
in this exact same thread. [music] So,
I'll be able to just watch one thread
and I'll be able to see everything that
they're doing. So, anyways, guys, just a
quick peek behind the curtain of the way
that I set this up and how simple this
really was. It's all running in Codex
with GPT-6 Astra [music] on high. So,
I'll see you guys in day one.
All right, guys, well, it is the end of
the first official trading day of the
challenge. It is 3:10 [music] Central.
You probably can't see that, but the
market just closed, so I wanted to do a
quick update on where we're at. So, at
the end of day one, we're at a total of
$9,991.
So, So, we lost about like
nine bucks. Now, I'm a little frustrated
because this is a 7-day challenge, so we
only have six trading days left and this
isn't much progress at all. I honestly
would have been happier if we lost like
500 today because at least I knew we
were kind of, you know, taking some
risks. So, what ended up happening was
it bought some Tesla and it had a stop
on it, and then the stop was executed
right away because it dropped. And it
did buy like nine shares, so it was a
lot of money. It was a little over
$3,000 that was, you know, at risk. So,
because in this challenge I'm allowed to
make tweaks throughout, I changed
something up. So, I basically was like,
"Hey, you know, this is a 7-day
challenge, right?" So, we only have six
days left. And now it says, "I
understand the urgency and I should have
acted on your feedback sooner." I've now
activated and verified the more active
plan. So, there's three entry reviews,
there's less restrictive filters.
Earlier, we were looking at the reward
to risk ratio being two to one, but it
lowered it now to 1.5 to 1. So, maybe
tomorrow we'll see some more movement in
our account because like I said, we've
only got six trading days left. I got to
go catch a flight, so I'll see you guys
for an update in day two.
All right, I'm currently at the Google
campus headquarters and I've got a day
two update for you guys. So,
let's get it to it. All right, so it's
day two and we ran into a bit of a
hiccup. Let me explain how this is
actually working and then I'll reveal
the day two results. So, as you guys
know, this is running on GPT-6 Astra
&gt;&gt; [music]
&gt;&gt; and it actually has a restriction in
there and it stopped trading for me. It
doesn't let me place trades. So, it
basically says, "Hey, I can help you
strategize, but I'm not going to
actually execute these automatically on
your behalf." And I tried to talk to it.
I tried to tell it that I wanted to.
It's still just not letting me. It's
like a model restriction. So, what I've
now set up is an actual GrokBot. His
name is Trader and he has this webhook
for when an email hits the account. So,
this GrokBot has its own email. So, what
happens [music] is Astra, when the
routine runs, it finishes off by sending
GrokBot an email and then GrokBot wakes
up, takes that email with the
recommendations, and then goes ahead and
processes the trade [music] through
Alpaca. So, it's still Astra with the
mastermind and with the strategy and the
research and then just delegating the
actual trade action to GrokBot. So, now
that I've got that out of the way, let's
talk about day two. So, this is kind of
frustrating because on day two, we're
pretty much right where we were after
day one. It literally did basically
nothing today and the daily change, as
you can see, was $0.21.
Now, this was the end of day two, so we
only have five days left and that's
that's pretty unacceptable. It's pretty
frustrating. So, because I'm able to
actually change up how this works, I
need to make this thing more active. I
need to have it wake up more often,
maybe every 30 minutes. I need to have
it be more aggressive. [music] It has
too many barriers right now where it's
looking through stocks and it's it's
understanding this might be a good pick
it basically just like rejects it at the
last second because it's too risky
[music] or for some other gate, it just
doesn't pass the final gate. So, I'm
going to kind of take off some of those
gates and see if we can't get a little
bit more money moving around tomorrow.
So, I'm going to make a few changes
&gt;&gt; [music]
&gt;&gt; and I will see you guys tomorrow and
hopefully, even if we're down a little
more, I think that'll be a win because
at least we know that the you know, the
Astro's getting a little bit more
aggressive. But the clock is definitely
ticking, so let me make some changes and
I'll see you guys tomorrow.
All right, guys. So, it is Sunday. I did
not do an update for day three on
Friday, so the market isn't moving
today, but let me show you what
happened. So, this is basically going to
be my day three check-in. Now, if you
guys remember at the end of day two, I
had to basically update the strategy a
little bit, shift it up to make our
agent a bit more aggressive because it
like wasn't really making any moves and
we were two days in, so I was getting a
little bit worried. So, we now do have a
little bit of money moving around. Let
me show you guys where we're at. So,
it's definitely nothing crazy at all,
but we are up a little bit. We're at
$10,018.
So, we're up about 18 bucks. Now, here's
currently what we actually have. We've
got almost $2,000 in HPE. We've got
1,200 bucks in Exxon [music] Mobil, and
we've got about $1,000 in Apple. And
over here, you can see that we're up
about 30 here, up about seven here, and
down eight over here. Now, this puts us
at about $4,000 of cash actually in the
market right now, and we still have you
know, 5,800. So, we've got about 60% of
the 10K still just sitting in cash, not
doing [music] anything. So, I think
tonight I'm going to talk to my agent a
little bit more and say, "Hey, you know
what? We're heading into day four. We're
you know, about halfway through, and
we've not really leveraged most of our
cash. So, let's see if we can get a
little bit more active here and you
know, just take on some bigger positions
or some more positions." Now, I think
it's a really great sign that we're
actually up about 18 bucks and here's
why. [music] In this challenge, I'm not
trying to tell you guys that I'm going
to be able to turn 10K into 15K in seven
days in the stock market. That's just
very unrealistic. I'm also not an expert
day trader. I don't have a day trading
background. So, really what I'm trying
to do here is I'm just trying to beat
the S&amp;P.
&gt;&gt; [music]
&gt;&gt; The S&amp;P 500 is basically a collection of
the 500 largest companies in the US, so
it just gives you a really good
indication of where the US market is
headed and how it's performing. And
right now, as you can see, go Bears by
the way, that [music] the S&amp;P, if I was
to have invested $10,000 into the S&amp;P on
Wednesday, September 9th, which is when
this challenge started, we would
actually be down money. We'd be down
about five bucks. So, in this challenge,
yes, I'm trying to make money, but
really what I'm trying to do is beat the
S&amp;P. If the S&amp;P is down 10% and we only
go down 5%, that's a win. So, anyways,
just wanted to give you guys that
context. Just wanted to give you an
update for day three. I will check in
tomorrow on Monday after the market
closes with a day four update. So, see
you guys there.
It's very hot. Good morning, guys. It's
It's day four of the challenge. The
market just opened, so let me give you
guys a quick update. All right, so last
time I checked in with you guys we were
actually up like I forgot like 17 bucks
or something, but we are now down. We're
down to 9876,
so not good overnight. Now, what's
interesting about 30 minutes to an hour
before the market opened, we actually
sold everything. So, now we have three
different positions that pretty much
just got executed. But, what you will
notice here is that we only have $2,000
just sitting in cash. [music] So, we
have about 8K right now actually in the
market working for us. Now, this is in
my opinion a good sign. I'm glad to see
that we have 80% of our portfolio is
actually actively in a position now
because yesterday you guys heard me and
you know, the day one and two I was
getting frustrated. I was like, okay,
nothing's really happening. We need to
get more aggressive. We need to actually
get our money working for us. So, we
have a lot of money in there today.
Let's see if we can't
have a big day. But, it's 8:50 a.m.
right now. The market pretty much just
opened. I'm about to hop into my
community Q&amp;A, but I will give you guys
an update later today when the market
closes. All right, guys. It's about 4:30
p.m. Central Time. It's time for an
update. This is not a very pretty graph.
Pretty much just consistently went down
all day. The daily change today was down
$225
putting us at about 9800 bucks. Now, we
do have a lot of the money in the
market. So, we've only got about 1200
bucks in cash. So, tomorrow hopefully we
can have all of this market value pick
up for us. Here you can see we're down
quite a bit here on CrowdStrike. We also
have a position in the S&amp;P ETF here,
which is interesting. You know, the
agent knows that one of the motivations
is to beat the S&amp;P 500, so kind of an
interesting call. I'm definitely going
to ask it why it did that, but we've got
some other stuff here. Nothing too
crazy, but we lost a lot of money there.
But anyways, down about 200, a little
over 200 on the day, down about 2.26%
and today the S&amp;P was down about 0.5%.
So, today alone we did not beat the S&amp;P.
We actually performed a lot worse than
the S&amp;P today. So anyways, I'm going to
talk to my agent a little bit, you know,
we're heading into day five, so we've
got day five, day six, and day seven
left. Three trading days left to try to
turn this thing around. I'll see you
guys tomorrow.
All right, guys. So, it is 9:42 a.m.
Tuesday, September 15th. So, this is day
five of the challenge and I had to give
you guys a quick update this morning
because our agent is certainly getting
more aggressive here. You can see that
we only have $8 in cash right here,
which means over almost $10,000 is
invested right now. So, this is what
we're currently working with. I woke up,
you know, my Grok Bot was sending me all
of these trades. We've got a lot of
money in the market right now. You can
see a lot of red over here. Daily change
is down 13 bucks at the moment, but hey,
I know, looks like we might be catching
some momentum here. So, right now we're
sitting at 9,000 783. I do believe we're
still a little bit behind of the S&amp;P and
obviously that's the goal, so I'm going
to hope we're holding strong through the
rest of the day and I'll give you guys
an update today as the market is closing
on day five. So, see you guys in a bit.
All right, day five has come to a close.
It's time for an update. After five full
days of trading, we are at a whopping
9,832.58.
Now, the good news is we were up on the
day. The daily change was about 36 bucks
and you can see that that puts us up
about 0.37 percentage points. Whereas
today the S&amp;P was down 0.45 percentage
points. So, we definitely beat the S&amp;P
today, but we still have quite a while
to go because you can see on day one if
we would have invested $10,000 into the
S&amp;P 500, we would have more money. We
would have 9,925,
whereas today what we have is something
more around this figure right here. So,
we are still behind the S&amp;P. So,
obviously we're right now losing the
challenge. We're, you know, a little bit
behind the S&amp;P by about 100 bucks and we
have two days to make that up. And just
in case you guys are curious, this is
where we're at as far as our positions
right now. We've got 63 bucks in cash,
the rest [music] is invested, and these
are the positions we currently have and
their market values. But it's really
interesting, right? I mean, today we
changed only 35 bucks, 36 bucks, and we
had like $10,000 of cash in the market.
And so that's why this challenge is
really interesting because obviously
when you're investing in the stock
market, unless you're doing some crazy
swing trading and crazy options with
tons and tons of money, you're not
really going to go up or down too much.
It's always more of a long-term
strategy. So if you guys are interested
in having me keep this thing going for
30 days, 60 days, 90 days, a full year,
let me know. I'd love to do that for you
guys and obviously make some videos
about it. But that is day five. I'm
going to check in with you guys
tomorrow. We've got two days left. So
let's see how this goes.
All right. So I wasn't actually going to
do an update yet. It's day six, you
know, it's about 2:20 p.m. I was just
going to do one later at the end of the
day, but I wanted to talk about this
real quick. So today, the Federal
Reserve unanimously voted to raise its
interest rates by 25 basis points, so
from 3.75%
to 4%. Now essentially what that means
is that borrowing gets more expensive
and investors may pay less for stocks in
general. Now the good news is sometimes
following a rate hike, all of these
stocks kind of feel like they're on
discount, like everything's on sale, so
you can buy when they're low, you know,
buy in the dip, and then they're going
to go back up. But in a 7-day trading
challenge, that really doesn't help us
very much at all. You can actually see
the S&amp;P pretty much right after this
announcement just started to drop, which
means unfortunately, so did our
portfolio. So as you can see, we are
down quite a bit on the day. So I'll
give an official update at the end of
day six once the market closes, but man,
not exactly what we wanted to see. All
right. It is 3:56 at the end of day six,
so let's do an update. Now
unfortunately, we're not looking too
good. Today was not a good day. You can
see that we're sitting at 9,759,
and we're down about 0.87% on the day.
We lost 85 bucks, and we've got $3,600
sitting here in cash. Now when the
announcement came out about the Fed
hiking rates, um Ashley decided to sell
a bunch of stock, so we had pretty much
all of our money in the market, but then
it sold a decent amount of money. We
were actually sitting at like 7K in cash
for about an hour or so. It decided to
pick up 80 shares of FPS, and we dropped
a little bit on that, but you know,
heading into day seven, we've got a lot
of work to do. Here's how the S&amp;P closed
today, and it was down 0.45%, which
isn't I mean terrible, but we were down
0.87%. So, according to Codex, if we
would have put our 10K just into the S&amp;P
at the start of this challenge, we would
only be down 9,857.
So, we would have lost about 140 bucks
so far, but we have lost about 240. So,
like I said, wasn't a great day. We've
got one more trading day to see if we
can come out on top of the S&amp;P somehow.
I'm obviously going to see if I can get
this 3,600 bucks that's sitting in cash
into the market, see if we can get that
working for us tomorrow. We need a huge
day tomorrow, so I'm going to talk a
little bit here to Astra. We'll see what
we can do, and hopefully I've got a cool
update for you guys tomorrow, and we're
able to bounce back to close off the
week. So, I will see you guys tomorrow.
All right, good morning, guys. It is day
seven. It's the last day of the
challenge. It's a super gloomy and rainy
day outside. Quick morning update. So,
as of this morning,
$10,012.
Look how much we've gone up. Just
kidding. We were up, and then we tanked
hard. So, right now we're actually
sitting about 9,868.
But man, look at this. I was so excited
to see this, and then boom, we tanked.
But luckily, Astra went ahead and sold
this position before we ended up tanking
more, so that helped. But we actually
just had a trade go through. We only
have $100 in cash, so we've got a lot of
money in here working for us. So,
hopefully we're able to come up even
more. We're up 153 on the day, but I'm
just going to sit here and stare at the
screen all day, just watch everything
happen, keep my hands off of the
keyboard, and I will check in with you
guys later. Hopefully, in the next
couple of hours we can pull ahead, and
we can win this challenge. But I'll see
you guys when the market closes. All
right, guys, it is 5:00 p.m. on day
seven. Let's take a look at the results.
So, unfortunately, we were not able to
hold on to the challenge high that we
actually hit the high on the last day.
We ended up 9,900. So, pretty much $100
down. Now, I think this is really
interesting because throughout this
whole challenge, we had to kind of find
our footing. I feel like we only got
truly five days of trading days because
the first two, the agent was way too
passive. And I think on day three is
when we really started to get like all
of our cash actually moving around in
the market, and we started to see a bit
more, you know, up and down. Now,
obviously, we are also just trading
stocks in this challenge, essentially
just owning, you know, kind of a piece
of a company. Whereas, if we were to be
opening up this trading strategy to
options, which is definitely possible,
where you're more so buying a bet that a
stock moves in a certain direction, that
could have helped us win or lose a lot
more money because you're basically just
you're risking a lot more money. So,
obviously, what I'm going to do is I'm
going to keep changing up the strategy a
little bit, and I'm going to keep this
going and maybe make another video for
you guys by day 30 because last time I
did this, it was 30 days, it was just
stocks, and we did beat the S&amp;P. So, I
want to see if we get more aggressive,
how much we can beat the S&amp;P by. So,
you'll notice that today we actually
were up a decent amount. Today, we got
182 bucks into the account, and [music]
we were up 1.87%. Now, the S&amp;P today
also had a decent day and was up 1.14%.
So, just on the day, we beat the S&amp;P. We
were up a lot more than the S&amp;P today,
but overall, the whole challenge,
we were not. If I would have put the
$10,000 into the S&amp;P on day one, we
would be at 9,980 bucks. But, today, we
are at 9,900.
So, the S&amp;P did beat us by about 0.8%.
Now, obviously, that is a loss, and a
deal is a deal, so one of you guys are
going to be getting a free VIP pass
&gt;&gt; [music]
&gt;&gt; to AIS Live October 17th and 18th. About
a week after this video goes live inside
of my free community, there's going to
be a post for this video, and you just
have to comment on it in order to be
eligible, and then I'll DM one of you
guys and say, "Hey, you got the
challenge." Or you won the challenge.
But, I'm sure a lot of you guys, based
on the title of this video, were
expecting that I was either going to be
up like 5K or down like 5K. But, that's
just not really what happens in the
stock market on such a short amount
[music] of time. Again, unless I was
doing day trading and swing trading with
like $20,000, $100,000, $500,000, that's
when [music] you see those massive
numbers of up and down. So, ultimately,
I don't think that just giving Astra
seven trading days was enough to really
know if this is a viable strategy. So,
I'm definitely going to keep this thing
going and bring you guys some more
updates in the future. But anyways, that
is going to do it for this one. So, I
hope you guys enjoyed or learned
something new. And if you did, please
give it a like. It helps me out a ton.
And as always, I appreciate you guys
making it to the end of the video. I'll
see you all in the next one.
Thanks everyone.
