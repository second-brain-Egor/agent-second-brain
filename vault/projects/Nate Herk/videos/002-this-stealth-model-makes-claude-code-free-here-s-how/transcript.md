Right now I've got all these different
Claude Code tabs running for completely
free. Because right here you can see
that the model I'm using isn't Claude,
it's Stealth OX Alpha, but I'm using it
within the Claude Code harness. So today
I'm going to show you guys how you
actually can set this up so you can use
free models inside of Claude Code, and
then I'm going to talk about if it
actually works and how good the stuff
is. I'm going to show you guys
everything and share my honest thoughts,
so let's not waste any time and just get
straight to this one. So right now I'm
inside of Herc 2, which is my AI
operating system, it's my second brain
with all my business context, and I've
got chats running in here for completely
free. So let me show you exactly how you
actually get this set up. It's super
simple, all you need to do is get an
OpenRouter account, and then you just
need to change one file inside of Claude
Code. What you're going to have to do
here is if you're using Claude Code in
the desktop app, you can't do this in
the desktop app. The reason is because
the desktop app overrides these settings
and forces you to use a Claude model,
which honestly makes sense. So what
you're going to do first is you're going
to go to openrouter.ai. If you haven't
used this before, it basically lets you
have one API key that can route to tons
of different models. As you can see
there are 500 plus AI models on the
site. If I go to the models you can
start to see that we've got certain ones
that are paid like DeepSeek, which is
still very cheap, or this new one that
just dropped today, which is what
inspired me to make this video, called
OX Alpha. As you can see it's $0 per
million input tokens and $0 per million
output tokens. You can also come in here
and you can search for something like
free, and you can see how many models in
here are free. Now obviously this comes
with some, you know, fine print. Maybe
they've got rate limits, maybe they got
a limit per day or whatever it is, but
there's a lot of free models in here
that you can play around with. And of
course they've got the ones that we all
love and know. So if I go to, for
example, Claude, you can see that
there's Opus 5, see that there's Fable
5, and also same thing with like GPT and
Gemini. It's got all the models in here.
So that's step one is to create an
account, and then all you're going to
have to do is go to your actual account
over here. You're going to go to
credits, and this is where you need to
basically grab an API key. So you'll go
to API keys, and you'll go ahead and
create a new key, and in just a sec we
will actually start to use that. Now
just to show you guys that this is
coming through free, if I go over here
to my, where is it, my activity, you can
see that my top API keys it'll show this
stealth test one, I've used 61.6 million
tokens just today by testing this out.
And if I go to my total spend and I come
over here to today, you can see that for
OX Alpha, it did cost me about 13 cents
total after all of that. But this was
after using it pretty much all day and
running through tons and tons of tokens
testing things out with it. Okay, so you
see where to get an API key, you see in
OpenRouter this model called OX Alpha,
it's from a company called stealth. So
if you want to read more about it, you
can click on to here and go to the
stealth model terms, and you can read
about this a little bit. But this is
basically an anonymous model provider.
So we don't know exactly where it came
from, we don't know if it's Chinese or
not. So think about carefully like what
data you're putting in here. If it's
really sensitive data, then you probably
don't want to give it to an anonymous AI
provider. That's not the point of this
video, the point of this video is just
showing you how to get it set up and how
it works, my honest thoughts on it. So
all we have to do is we are going to go
into a project. We're going to do this
in VS Code. So if you typically are a
desktop user for Cloud Code, you're just
going to have to deal download some sort
of IDE, or you can run this in the
terminal if you want. But if you
download VS Code, it's completely free,
and then you just open up the terminal
in here or the Cloud Code extension and
you use
Cloud Code, then you will be able to do
this. So inside of your .cloud, we
typically have a settings file. So right
here is my settings file, and inside the
settings file we have uh a section
called ENV. So kind of like environment
variables. Now in here, what you need to
put in is this stuff. I'm going to copy
and paste this into the description of
this current YouTube video, you'll grab
that, you'll put it right into your
environment variables inside of your
settings file, and all you're going to
have to switch out is your Anthropic
auth token. And this is actually just
going to be your OpenRouter key. So
you'll go back into OpenRouter,
you'll go to your activity like I showed
you, you'll go to your API keys right
here, create a new key, copy that, go
back into Cloud Code and paste that in
right there. And then, if you want to
use the stealth model, which is what I'm
showing you right now, you basically
just have to copy this and put it in all
of these slots. So, basically the way I
found that is back in here when I go to
my model, I go to OX Alpha, I just
copied the name of the model right here,
stealth/ox-alpha.
Now, let's say you wanted to switch out
the model for a different free one, you
would basically just have to find the
free one you want. So, let's say we
wanted to try something like
GLM 5.2, we would basically just click
on copy right here, and then we would go
into the settings file, and every
instance of stealth OX Alpha, we would
just switch that out for this model, GLM
5.2 free. You'd save all that and then
you'd be good to go. So, I'm going to
unsave that. And then, when you open up
a new session, it should show right here
that you're using this model, and it
should also show down here if you have a
status line set up. But, that's how you
know that it's actually working. And by
the way, real quick, OpenRouter seems to
switch out these models that are free
sometimes, so maybe by the time you're
watching this video that OX stealth
Alpha model isn't here anymore or it's
not free. So, what you can do is
obviously you can come in here and
search free, but also OpenRouter has one
called a free models router, which is
the simplest way to get free inference
because this basically just selects free
models at random, basically whichever
ones are available. So, it shows you
some of the models that it will
constantly route to. So, if you use this
whole method where you use this as the
actual model inside of your settings, if
you go back into there, and you were to
actually just put OpenRouter free inside
of all these
places, then it would be constantly
every single request just routing to a
different free model on OpenRouter. So,
I just wanted to throw that out there in
case you're watching this video a while
after I made it. So, anyways, let me
just show you two quick things that I
did once I opened this up, and show you
how this works. So, I did a slash goal.
I said, "Look inside my project that
lives here." So, I told it to go to a
different directory. I told it to create
me a simple but professional and
on-brand landing page. It needs to have
all the details of the different
products, and it needs to be clickable
and on-brand, all that kind of stuff.
Now, what happens is that it does the
normal Claude code loop, right? cuz it
can acknowledge the goal, it can think,
it can search files, it can write, it
can use all these tools. But, what kept
happening was I kept getting this API
error, and it said upstream idle timeout
exceeded. So, I realized that this was
happening because it was trying to like
write so much and look through so much.
So, I told it to work in smaller chunks,
and then it basically ended up being
fine, and it kept going, and it wasn't
an issue. But, when you are using these
free models on OpenRouter, that tends to
happen for multiple different reasons.
Maybe tons of people are hitting the
API, maybe it's trying to do too much.
Sometimes that just happens. But,
anyways, I finally got it to acknowledge
why that was happening, and it kept
going.
And it finished up, right? So, it not
only did it create the landing page, but
it also did verification. So, it did
technical verification, functional
verification, and visual verification.
But, it also took 6 hours. And I know
for a fact this would not have taken
that long with regular Claude. It's just
right now it feels very, very slow. So,
anyways, here is the actual site. It's
not too bad, right? Like it's got the
logo, which is correct. It used the
right packaging. So, I told it to use
these. I actually wanted it to use the
real product shots, so I wanted it to
use like these images instead that look
a little more real. But, I accidentally
pointed it to the packaging. So, it used
the packaging, which obviously doesn't
look like a real can. But, hey, this is
what I told it to do, and that is what
it did. So, I'll give it credit there.
It also did use our brand guidelines.
So, obviously the logo, the color
scheme, the spacing, all of this stuff,
the typography, it used all of this,
which was also really good. If I keep
scrolling down, you can see that we have
a little sliding bar here. We have two
drinks, one can, coffee plus protein
shake equals Perk Form. All of this
information is correct. We have these
different products, and we can click
into these. So, Bold Mocha, I can view
this. I can buy a single can, a 12-pack.
I can add it to my cart, and it actually
goes in my cart. It's functional, right?
Like we have the roast, the sweetness,
the body, we have all this. We can go
back to the shop. We can go into another
flavor. Same exact thing, we can add
these to the cart, and we can see more
facts about all of these. It even made
the nutrition facts. So, it's not too
bad, right? For front end, and for
digging through all that, it's not too
bad at all. Like I said, the issue here
was just how long it took, because this
took 6 hours. And so, that's kind of the
theme right now that I'm finding is if
you wanted to build an app, build
software, if you wanted to do some deep
deep deep technical stuff, these models,
these free models, these small local
models are not going to do it nearly as
well as Claude or GPT. It's just not.
That's the truth. But for knowledge
work, it will do stuff for you very
well. The way I feel typically is Opus 5
or GPT 5.6 solar or whatever you're
using to drive your day-to-day is
probably overkill. Like most of the
tasks that you're doing on the
day-to-day are not that complex. It's
just when you really need to think about
scoping out an entire project or having
a model be an orchestrator of tons and
tons of dynamic workflows and
sub-agents, that's where you're really
going to feel a big divide where you
need a more powerful model like an Opus
or a GPT. So, let me just show you a few
more examples and that will make sense
to you. Here's another one that I did, a
slash goal. I wanted it to go to my
YouTube channel data and pull a report
for me about the past quarter and over
the past year. I wanted to also give me
a prediction based on my audience, my
channel, my niche, what I should be
prepping for as far as content in 2027
predictions, and I wanted this to be a
final deliverable as a Google Sheet. So,
it went through the loop, it did all the
stuff, it took This one took also 6
hours. So, it just took a long time and
this would have probably only taken
20-30 minutes with a regular Claude
code. But the actual deliverable is not
too bad. So, it was prepared on today's
date for this channel with this many
subs, these sources, a data note,
there's different tabs. And when you go
through these, it's not bad, right? It
was able to look through my data. And
also if you'll notice, I'm in a project
right now called free Claude code and
basically there's nothing in here. So,
it had to investigate, dig through my
other projects, and it was able to find
that I had all of these like scripts and
API keys already written. So, it found
those and it used those to actually
access my YouTube data. Because in here,
there's not even like a Claude that I'm
doing that says who I am, right? This is
basically just an old Claude that I'm
doing that I set up about Gemma 4 that
has nothing to do with what we're doing
now. So, I will give it credit for that
as well for being able to use the
harness and use its intelligence to
figure out how to actually get the job
done, especially because I gave it a
slash goal. Anyways, the output's not
bad. It found all this stuff. Here was
the quarterly report. It pulled per
month views, watch hours, subs, the
average viewers, the top videos, all
this kind of stuff. It even went into
different sources. It went into
different countries, audience, devices,
all this kind of stuff. It did the exact
same thing for the year. It looked at
every single video. So, all 400 and like
69 videos that I've put out on here,
maybe 468. And then 2027 outlook. So, it
did a good job. Like I said, it's not a
terrible model for knowledge work. It
did a decent analysis. It pulled all the
data. It it was a little bit like
pragmatic and solved its own problems,
but it took way too long for something
like this. Like arguably, I could have
done this manually
about the same, maybe even a little
quicker. And now let's jump back over
here. I went to my actual Herc 2 project
and you can see that I said, "Hey,
here's a YouTube video. I need to
process this for me. I need you to put
this skill in the database." So, you
know, I have this sheet that I have all
my resources in and it was able to look
through it, right? It found the skill
right away, which means that because
it's a model, even though it's a foreign
model in the Claude Code Harness, it
still knows to look through your Claude
and MD. It still knows to invoke your
Claude skills, stuff like that, your
memory. So, it found that skill. It used
it. It did all the right things, but
this has been going for way too long.
This normally takes normal Claude like 5
minutes if that. Anyways, it found these
skills. It wrote this stuff. It just
worked a lot and then it said, "Okay, so
I stopped trying this retry loop and I'm
handing this to you. Everything local is
done, but I'm blocked by Claude Code
infrastructure issues." So, it got
blocked for some reason. But what else I
noticed that's kind of cool is that it
created like a cron right here. So, it
tried to create a cron job for itself to
basically like retry this every, I don't
know what this is, maybe 10 minutes,
maybe 20 minutes. That's kind of cool
that it wanted to retry, but ultimately
it stopped and said, "Hey, I'm blocked."
But it took 44 minutes to get there,
almost 45 minutes to get there. So, it's
just very slow. Also, in the second one,
I asked it to go to school. It pulled
166 support needed threads from my
community AIS Plus and it found the
three common threads, 30 posts about
this, 15 posts about this, 35 posts
about this. But, this took 25 minutes.
Not too bad, but this normally happens
way quicker with regular Claude. But, it
was able to invoke my regular skills and
do my regular knowledge work. And then,
you can see over here, another instance
where this keeps happening. I told it to
do some research on OX Alpha stealth
model, and I told it to create me an
HTML of what happened. It hit the error.
I told it to keep going, and it hit the
error again. So, sometimes it just runs
into these issues, but the cool thing is
the good news is it can invoke skills,
it can use Claude code fetch, it can use
Claude code web search. So, really it
can do things that work inside the
Claude code harness. It's just going to
be a little bit slower, and you're
probably going to run into some issues
like this. But, hey. I honestly do think
it's really cool. If you run into a
situation where you're out of your
credits for the day or for the week, and
you need to keep working on some light
things, then chuck in one of these
models. Like, you might as well just
play around with a little bit, as long
as you're being safe about the data
you're sending to these models if you
don't know where they're coming from, or
maybe you go to, you know, open router
and you switch out the models. Let me
just show you real quick how that would
work. Let's say I wanted to use this
one. Like I said, I copy this. I'm going
to go back into this one.
I'm going to just change out the model
right here, and I'll only do it once
right here. I'll do it here. And then,
if I save that, and then I open up a new
terminal right here, it now should have
updated. This one should be using ZAI's
GLM 5.2 free with API usage billing.
Now, the reason you want to switch all
these other ones out, too, is because if
your session invokes
different sub-agents, and it wants to
make like a Sonnet sub-agent, it would
do that with stealth. Or, if it didn't
open sub-agent, it would do that with
stealth. So, that's why you want to
switch out all of those when you want
all of them to actually be the same
model. So, anyways, that's how this
works. I hope that this opened your
guys' eyes, and I hope that this all
makes sense. Go ahead and give it a try,
and let me know if you're able to find
some good use cases with this type of
stuff, but it's definitely worth at
least a shot. And if you guys want to
see how you can do this type of stuff
with completely free local models that
you would run like right down here on
your machine, then let me know. I'd love
to make some more videos on that type of
stuff as well. But, that's going to do
it. So, I hope that you learned
something new, or you enjoyed the video.
And if you did, please give it a like,
it helps me out a ton. And as always, I
appreciate you guys making it to the end
of the video. I'll see you on the next
one.
Thanks, guys.
