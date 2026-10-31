---
type: project
last_accessed: 2026-10-30
relevance: 0.98
tier: active
---
Okay, so this one's a little bit
different because today what I did is I
gave Claude Code this website which is a
horrible coffee shop website and I
literally just told it make it better a
100 times in a row. So what I want to
talk about today is basically what
happened. I did this with sonet 5.5 on
medium effort and I did it with obus 5.5
on medium effort and I just said make it
better 100 times. So I'm going to show
you guys what happened. So as you guys
know this is the original site. I had to
make something completely awful and ugly
for them to start with and then this is
the exact prompt that was shot off to
them 100 times in a row. So it says,
"Look at the site first, then innovate.
Think about the user experience and
think outside the box. Make one bold
change that improves conversions or the
look and feel, not a small tweak. Use
any tool you have. You must ship a
change every time." And the reason why I
had to be so specific with this
prompting is because when I tried this
before, it would just stop at like 20 or
25 and be like, "Hey, nothing else can
be done." And so I had to basically
force it to make a change every time.
Now, the reason I wanted to do this is
because lately I've been having so much
success building different AI pipelines
when I've been using inspiration from
other people or other proven methods
because I think AI is really, really bad
at thinking outside the box. And a lot
of us would love to just be like, "Hey,
make this prettier." Or, "Hey, make
this, you know, smoother." and and just
kind of give these big vague goals which
are good but I think you hit a cap at
maybe let's just call it like 80 out of
100 and so I think to get to more of the
90s you know high 90s 100 out of 100 you
have to be the one that's applying the
taste and helping innovate so that's why
I wanted to try this experiment now
another important thing to know before
we hop into the results is that it ran
in a clean room every time so fresh
session no skills no cloudmd no plugins
no memory each model had basically just
its own knowledge and any built-in tools
so it looked at the site like I head. It
thought about it and then it decided,
okay, here's one thing that we can do to
think outside the box to improve the
site and then let's ship it. So, here's
the little local host that it spun up.
You can see that I've tried different
rounds here and we're going to be
looking at Sonnet on Medium and Opus on
Medium. So, let's start with Sonnet. You
can see on this left, it's going to show
you every single round, how many tools
were called, how many lines are in total
the site. But really, what I want to be
looking at are some of the milestones.
First of all, what you can see is that
Sonnet ran and this would have cost us
$29.93
via API billing. Sonnet also created 11
images and two videos in this site. But
anyways, I'm just going to go ahead and
switch this over to the milestone view.
And that's going to show us when major
things happened. So, in round one, we
obviously had a major milestone. There
was the biggest jump here because we had
it was the first time it looked at its
own site. It had the first ad generated
image, which is this background right
here. It was our first JavaScript and it
was our first mobile ready. So, here is
V1 of the site. Been there, coffee,
being their coffee. We have an image in
the background. And I can actually open
this up in a new tab so we can look at
it a little bit better. We have a very
simple looking punch card, very boring
font. All this stuff is just very, very
plain. Nothing too crazy. If we go to
round two, we had our animation come in.
So, this is where we had a first
animation. Let's see where that is. I
actually think it it was just this when
we have our order and we scroll, this
little order bar sticks. So, if we
started filling things in and then we
scroll down, we would get that to be
sort of like stuck here. And that's not
bad, right? That's a nice little
innovation. We didn't have another major
milestone until round seven. And you can
see here the lines of code went from 253
up to 419. And this now says the
milestone was first working image on the
page. So, it looks like now in the hero
section, we have an image up here. Um,
and maybe this wasn't what it's
referring to, but we can choose things
for the menu. Where is the working
image? Maybe it's these things. when you
add them into the menu, you can actually
see a picture. I think this was probably
the milestone that it's referring to.
But anyways, you can see it's just
slowly making tiny tiny little changes.
It's definitely getting better, but it's
definitely not great still. Now, we have
another milestone at round 24. 778
lines. We have a first AI generated
video, which looks like this background
right here that we see where we now see
this little animation coming through in
the background. We also see that this
has been improved. We can also see that
this has been improved. We got a nice
little scroll animation with a, you
know, a static image in the background,
which I think is a nice touch for some
depth. We also have this has been
improved a little bit. The order now
looks more like a receipt or like an
actual ticket rather than just a little
weird animation box. And yeah, we can
see that we're definitely getting things
added. We can see that our punch card is
showing up. And yeah, it still keeps the
same branding and everything, but we're
adding little things. And actually the
final milestone here was round 32 where
if I open this up it says this was the
first form. So we have an actual form
now it looks like where we can order
online maybe and then we can order ahead
and go pick it up. So we can maybe
schedule our order here. This takes us
up here where we can add things to the
order. Let's see if I add it. Then we
can actually place that and boom we
could then go pick it up and we have our
food slashdrink. So functionally it has
increased the user experience a little
bit. It hasn't done anything too crazy
as far as the site, but you can see that
each round we have had some sort of
small innovation. Now if I turn this off
milestone only view, obviously there's
tons of other rounds. It didn't actually
say anything was big enough to be a
milestone from rounds 32 all the way to
round 100. Now what's interesting is
right here you can see API value per
round. You can see lines of code and
what happens is the API value is like
kind of going up and down and the lines
of code every single round is steadily
increasing kind of linearly and what
that tells us is like it's adding a
bunch of code and we don't know if
things are actually getting that much
better. So here is the round 100 version
from sonnet. We can see we had a little
animation there with ordering ahead and
walking in line. I'll refresh in case
you missed that. We have a nice little
floating bar that kind of moves up and
down. That was probably one round of
innovation. It's got a little glow to
it. Now we can see the full menu. We
have some hero stats up here. We can
switch between help me pick up, browse,
or just typing in your order. We also
have a little popup now. So, there are
definitely other things. We even have
like only two left, baked at 11:00 a.m.
So, it's definitely getting better. It
also decided to make this little order
thing um scrollable, too. So, I like
that. We can see we even have now some
testimonials in here. We can order their
usual orders. We have some little leaves
falling down here, the maple cinnamon
latte, and all of these other things.
We've got a scroll bar or a scroll
animation bar of actual products in
here. So, more videos, more videos. We
can see how long the line is. We can see
the typical busy hours, all this kind of
stuff. So, the question really is like
at what point is this too much, you
know, like what round would we have
stopped and been like, "Okay, you know
what? Round 65, this is good. Anything
else that you keep adding is just going
to be extra fluff. We're not going to
need it." Interesting. It actually looks
like it took something away. So here is
round 65. We have like this little
navbar on the right. But what'll be
interesting is if we went back to round
100. Did we have that? I think we don't.
So it ended up actually taking away a
feature that it didn't like which is
pretty interesting as well. But I think
at a certain point it just like starts
overengineering because obviously what I
told it to do is you have to ship
something. So it starts forcing changes.
Like here you can see this is round 74.
Look at this font. If we go to round
100, you can see that that font is
different. So at one point I was like,
you know what? I'm just going to change
the font. So, very, very interesting.
But let's pivot over now to Opus. Real
quick, guys, I've got this completely
free website design skill that I'm
giving away. I use this for every single
website that I build, including our AI
Automation Society site, which I think
is pretty slick, and I absolutely love
this website. It's called ScrollCraft,
and it understands things like scroll
driven animations and layering, but also
it has things in there like taste,
typography, spacing, depth. It's just a
really good website design skill in
general, and it's completely free. So,
the link for this will be down in the
description, but let's get back to the
video. All right, so same exact thing.
We're going to start with the milestones
only, and then we'll look at some of the
other ones, but this one cost $137,
54 AI images, and three AI videos. So,
the first round, V1, first time looking
at its own work. First AI generated
image, first animation, mobile ready.
So, it definitely made more progress on
round one than Sonnet did. We have a
picture here. We've got the classic
anthropic font. We have the menu, which
we can select some items, and we're
already getting a bit of a popup down
there. We can text our order. Once
again, it decided to do a punch card.
Well, it probably was on the original
site. We've got the hours. Okay, cool.
So, very bland, very boring, nothing too
crazy. Round seven, we had our first AI
generated video, which looks like this
background of the hero section, and it
starts to look a little bit more like
that sonnet version. We have a very dark
theme down here. Two days off, the
roster. We can choose different flavors.
We have a bit of a menu now with some
different AI generated images of these
items, punch card, and visit us. So,
nothing too crazy, just the video. Now,
round 15, we had our first form. So, now
we have the ability to actually fill
something out and we can start to like
send in this order. We can also do a QR
code, which is pretty cool. Actually,
let me see what happens when I fill out
that QR code. Oh, interesting. So, when
I scan the QR code, it fills out a text.
I don't know if you guys can see this.
It puts my order that I put in the
actual site and it sends it to the
number. So, I could literally just text
this order punch card one of nine after
this order. Wow, that's actually not
bad. That's pretty cool. So, that was
our form. Nothing else is too crazy.
It's starting to play with colors a
little bit differently on different
sections. It's also showing us that this
is roasted 20 ft from your cup. So, we
get a cool little animation there, but
besides that, nothing too crazy. And
then the last milestone here was round
32 where we have our first canvas or
webgl. And I actually don't exactly know
what that means, so I'm just going to
call Glido real quick. Hey Glido, what
does a canvas or WebGL mean inside of a
website? We should see up here, Glido
will shoot that off to the web. Canvas
is an HTML element that lets scripts
draw graphics like shapes, images, or
animations directly on a page. WebGL is
a JavaScript API that uses the browser's
graphics hardware to render 3D graphics
inside the canvas, enabling complex
visuals and games. Okay, interesting.
So, let's see if we can find that. I
wonder if that's this. Maybe it's this
sort of animation where we can say, you
know, what are we looking for as far as
something easy or waking me up and sweet
and cozy? So, wherever you decide to put
this, it will basically say, "Hey, this
is the drink that's most close to what
you're looking for." So, that's actually
pretty cool. I think that was one of the
innovation times where I actually would
have kept that change. But, I feel like
the majority of the times when I'm
asking Opus to just innovate, I'm not
going to actually accept that change cuz
I maybe think it's overkill. So, I like
this little whiteboard. I think that
there's too much text on here. Honestly,
this is supposed to be like people's
orders, which I think is kind of cool.
But anyways, we can start to see
different timing and when we'd be able
to get it. That's pretty cool. good for
the user experience. Also, we can like
reserve seats, which is pretty
interesting. Not too bad. Where to pick
it up from and how long it'll take us.
So, anyways, I really like this text at
the bottom, too. So, now we're at the
point where like I might be okay with
this. I might stop and be like, this is
already a lot, but we still have 70
rounds to go, 68 rounds to go. So, let's
go out of this view and let's first look
at the very finished version. So, round
100. If I open this up in a new tab,
this is going to get overwhelming. You
know, Opus was forcing iteration here.
And there's a lot going on. There's
leaves. The background has changed.
There's so much text. So, this is the
point where it's like, yeah, this is AI
slop, right? Like, look at this right
bar. Look how much we have to go
through. Look how much we have to go
through here. We can carve a pumpkin if
we choose a small knife or a big knife.
You've got to be kidding me. And this
doesn't even work properly. Well, I
guess it kind of does, but not really.
Like, you have to start at the bottom.
So, that's kind of buggy. It didn't
really get tested very well. But as you
can see, we're just at this point now
where this is definitely overkill. We
don't need all this info because people
probably just want to grab their coffee.
And this se this section doesn't even
work anymore either. So, it ended up
breaking some of its own stuff. It's
also looking at like caffeine, where it
will be in your system, how you'll be
able to sleep. You can also toggle this
on if you want to go to Spanish, which
didn't even switch this to Spanish. So,
it ended up trying to force so many
changes that it broke the site and it
just killed the user experience. Like,
this is just obviously way too much here
and we're not even halfway through the
site. We can now have music. We can
choose so many different things in here.
So many different Like I like this
review board actually. I like the vibe
of this, but it's just too much, right?
Like it's gonna get lost in here. I
think you guys get the point, right?
Like it's very interesting just to see
if you force Opus to keep working, it is
going to just overengineer things. It's
going to overkill them and you really
need to be there to give some guidance.
So hopefully this was interesting to you
guys as well. If we look at the final
stats, Opus ran for eight and a half
hours. Sonnet ran for almost two. Opus
spent about 137 bucks. Sonnet says
Sonnet spent about 22. Obviously, if
this was API billing, I did this on my
subscription, but obus 5.5 ended up
having 21,000 lines of code in this site
and Sonnet had less than 3,000. We have
a difference in AI images and videos.
And the first video for each of these
models, Opus did it in round seven and
Sonnet did it in round 24. Now, once
again, I think this is really
interesting because it didn't utilize
any skills. It didn't look at any
reference sites. It just tried to do its
own stuff. But what really really
shocked me, which I was honestly kind of
upset about, is that it didn't use the
internet at all. I thought I put that
here as a bullet point. I guess I
didn't. But it didn't do any web
searching. I thought for sure that it
would be web searching websites and
maybe looking for components at
something like 21st. Or looking up
websites that are winning awards and try
to steal inspiration from that. But it
didn't do web search. None of these
models or I guess not none of them.
Neither of them did web search which
really really shocked me especially when
I kept saying innovate innovate think
outside the box. I thought that it was
going to do some research to pull
inspiration from but it didn't. So the
model sets the ceiling and the prompt
sets the direction. It was obviously the
same prompt here but the different
models came out with very different
results. Innovate without a vision turns
into adding. They started adding stuff
and forcing stuff in when we didn't
actually need it. It also really really
wanted to improve conversions. So it
tried to upsell everything. It tried to
force ordering. It tried to make it so
so seamless but it was too much. it was
like a hard sell rather than more of
like a soft close. So, very, very
interesting. Like I said, this isn't
going to change a ton about the way that
I work, but I just wanted to know and I
hope that this was interesting to you
guys as well. So, if you enjoyed the
video or you learned something new,
please give it a like. It helps me out a
ton. And as always, I appreciate you
guys making it to the end of the video
and I'll see you all in the next one.
Thanks everyone.
