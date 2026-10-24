---
type: project
last_accessed: 2026-10-23
relevance: 0.98
tier: active
---
So right here you can see that I've got
Jeff Bezos, Paul Graham, Alex Rossi,
Gary Vee, Dan Martell, Gino Wickman, and
Warren Buffett all discussing a business
question that I had. You basically shoot
off a question with different options
and all of these different council
members will kind of come together,
roast your idea, and help you think
about it in a different way because each
one of these seats has one specific
question that they're focusing on. And
now you can see what's happening is
they're actually debating with each
other. So Jeff Bezos was debating with
Gary Vee. Same thing with Paul Graham
and Gary Vee. Now we've got Alex Herozi
going after Gary Vee too. And wow,
everyone's deciding to pick on Gary Vee
in this roast room. This is crazy. There
we go. Warren Buffett goes after Herozi.
But the point is, like I said, everyone
has their own question they focus on. So
Warren Buffett's question is, what does
it do to cash risk and long-term value?
Alex Herozy's question is, will people
pay? How much? And how do we close? And
Gino Wickman's question is, can the
business run this without the founder
holding it all together? Now, after all
three of those rounds happen, we can see
that we have a final verdict, which was
option C. And then we can also download
a PDF, which allows us to read this, and
we can sort of look at this more in
depth. And we could also share this with
our team if we wanted to. Now, this is
really just a visual layer on top of
what actually goes on in Cloud Code,
which is basically just running a bunch
of sub aents based on these different
council members that I have created. So,
you don't need this local host open in
order to run and use this, but it's just
a nice visualization of what's going on.
And this is completely customizable,
meaning you can switch out different
council members and you can build other
ones, too. In fact, inside of this repo
that I'm going to give you guys, there
already are a few other ones, too. Hey
Claude, what are the other council
members inside of our roast room? And so
that's Glido actually shooting off a
prompt right now to Claude Code, as you
can see. And then it'll show us who the
other council members are. Claude Code
comes back and says there are 11 seats.
We have the default seven that you're
seeing here. And then we also have
Naval, Cody Sanchez, Sarah Blakeley, and
Leila Hermosi. And of course, you can
build as many other ones as you want. So
that's a new feature of Glyo where we're
able to actually orchestrate different
chats between different coding agents.
If you want to try it out, you can get a
free month using the link in the
description. But anyways, just wanted to
show this off to you guys and let me
break down how this actually works. So
this is a repo called the roast room as
you guys can see. And basically we have
these seven different advisors as well
as four extras and I'm probably going to
keep adding more in the mix as well. But
what I wanted to show you is the
advisers. What are these council
members? What do they actually live?
They're actually just a bunch of sub
aents. So if I go into the claude,
actually let me zoom in a little bit
more. You can see that we have agents
and in here we have one markdown file
for each of these sub aents. So Bezos,
Blakeley, Buffett, Gary Vee, Graham and
all the way through. And if we open one
up so you can see what it is, it's
literally just a markdown file that
holds information about the sub aents.
So for Jeff Bezos, for example, how he
thinks, what are the sources that he
references, how he makes decisions, all
that sort of stuff. So that when I
actually shoot off a prompt to the roast
room, it's going to go through the
different council members and it sort of
adopts their personality of how they
think and how they make decisions, what
they, you know, and it's able to pull
from things like their actual
conversations, their lectures, their
books, their principles, things that
they put out there publicly, articles,
stuff like that. So what you'll notice
is they will all have their own agent
file, which isn't really that long. It's
some things like how you debate, how you
talk, your lens, but the really
interesting stuff here is the brain
right here. So, we can see all the sub
aents, but if I actually go into the
skills in this repo, we can see that
there is a roast room folder that has
brains. And once again, there's a folder
for every single council member that you
want to spin up. So, if we, for example,
open up Laya Hermosy's brain, we can see
that she has hot books, frameworks,
positions, principles, sources, stories,
and voice. And it's pretty much the same
thing that all of these other council
members have as well, but they all
obviously look different. The content is
different. So if we open up Ila's hot,
what happens is we can see her pillar is
can your team and your leadership carry
this and who has to change. It shows us
what this was built from. So for
example, Leila was built from 48
sources, about half a million words from
2021 to 2026. 14 interviews where she's
the main guest and 34 videos of her own
on leadership and things like that.
Every person here has eight rules. They
decide by frameworks, decision loops,
things like that. Obviously, any books
that they've written, frameworks that
they talk about frequently and that they
quote, their positions on certain
things, pricing, discounting, raising
money, debt, their principles, different
sources that it actually pulled from,
specific stories that they might talk
about in videos, interviews, things like
that. And every single one of these
brains for the individual people is
built the exact same way. If we open up
Dan Martell, we can obviously see that
he's got books in here as well. We can
see that he's got frameworks that he's
using all the time. You can see the
buyback principle, the buyback rate,
time and energy audit, the drip matrix.
All of this stuff should sound familiar
to you guys if you have followed, you
know, Alex Heroszi or Dan Martell value
equation, grand slam offer, all of these
things that they actually talk about all
the time. A quick break to tell you
about the sponsor of today's video, Fish
Audio. Now, anyone who's tried AI
voiceovers knows that the words come out
right, but the delivery doesn't always
because it might read a joke or a
warning and an apology in the exact same
tone of voice. So, Fish Audio has a new
model that is their most emotive yet,
and it's called drama 3. You direct it
the way that you would direct an actual
voice actor, which means that you can
write the direction in plain English
inside the text, like slowly realizing
something's wrong, and everything after
that tag will follow that direction. So,
one line can start calm, and it can end
in a panic.
&gt;&gt; Thanks for calling. Your order is on its
way. Wait, that's not the right address.
Who approved this workflow?
And the tags work in other languages,
too. It also generates full
conversations. You can give each speaker
a voice. You can mark who's talking. And
every character keeps their own voice
across the entire scene. Just run it one
more time.
&gt;&gt; Of course, that'll be attempt 47.
&gt;&gt; So, if you're putting it on video, the
streaming endpoint sends word level
timestamps back with the audio, so your
captions line up exactly with the
speech. Now, on the build side, you set
the model to drama 3 in the fish audio
API. They also have an MCP server too,
so you can connect it to cloud code or
codecs. And they also have an official
NAND node. So if you're building
something that talks like a voice agent
or a game character or just narrating
your videos, then try Drama 3 on the
Fish Audio API with the link in the
description. Huge thanks to Fish Audio
for sponsoring this part of the video.
Now, let's get back to it. And then I
added this new skill called New Roaster,
which basically just lets you build new
roers. So for example, if I came in here
and I was like, "Hey, new roster." and
we wanted to do, you know, Elon Musk and
we shot that off. This will basically
create Elon Musk's brain and his agent
file and all of his sources. It will
build him out and also build him a
little cartoon character that will show
up in the actual roast room itself
exactly the same way that all of these
other Roast Room council members have
been built out. So, you can keep scaling
this thing up. And obviously, I'm going
to let this thing build out Elon and
then I'm going to add that into the repo
so you guys can all use Elon as well.
So, while this is building out Elon, as
you can see, let us do a new session.
So, open up the roast room. That's
pretty much all we have to do is ask for
it. And I'm just going to switch this
back to Opus here. And it's going to
open up the roast room. We'll open it up
in the local browser inside of the
desktop app. And then we will shoot off
a prompt so you guys can see how this
actually works. Now, once again, you
don't need this visual interface opened
up. It will obviously run the sub agent
roast room just the same, but it's nice
to see. But one thing that I will say
about actually spinning up a roast room
is typically you want to put in a
decision. You want to put in options. So
two or three options. You want to give
it context so that they can actually
reason through it and make a better
call. Right? So let me just shoot off a
quick example. We are looking at hosting
another in-person event in the summer of
2027 and we're trying to figure out
where to do it. We've been, you know,
analyzing different options like San
Francisco, Salt Lake City, Austin,
Chicago. We obviously want to be able to
get good sponsors there, local
incentives, get a lot of people there,
and, you know, so airports should be
important. Um, public transportation,
good restaurants, good activities to do
outside of just having the event, things
like that. So, help me figure out where
this should be and do this on the roast
room council. So this natural language
request should be just fine. But you
could also couldn't come in here and do
a slash roast room. And then you could
just invoke this like that. But we will
go ahead and just get rid of that for
now and shoot that off and it should be
good enough. One thing that this will do
is it will help you figure out what
would be the best council members to
have for this specific debate. As you
can see, it's going to load the skill.
It's going to gather event and business
context. So it will ask you questions if
it doesn't feel like it yet has enough.
And then it will actually go ahead and
run the debate for you. So, you can see
it is going to ask me a couple questions
here. It has four questions that it's
asking me. And by the way, we already
did book this event in Salt Lake City,
June 16th through 20. So, if you guys
want to attend, then definitely check it
out. But for the sake of the example,
I'm just going to pretend that none of
this has happened yet. So, I'm just
going to say not signed, open choice. It
says, "What size and budget should the
council plan around?" And I accidentally
just skipped through those questions,
but the last one says, "Who sits at the
table?" And it gave me a recommendation.
And it also lets you play with it if you
wanted to put different people in. So
that's part of it is thinking about who
should actually sit on the council for
your specific debate. But now that's
going to be it. It's basically going to
run. It's going to process this. Even if
this was closed, like I said, we would
have sub agents that would be going
through and doing this no matter what.
And the reason I decided to do this with
sub agents because when I actually
started doing these roasts, I started
doing this with agent teams. But the
reason I'm doing sub agents now is
because I found after doing lots of
testing that agent teams was more
expensive for a minimal amount of actual
value ad. So doing sub aents works
pretty well because they start to
actually talk to each other and stuff
like that either way. So it works just
fine. Now in this case you can see that
we took out Dan Martell because his is
more about like protecting the founders
time and we put in Naval and his
question is does this build leverage and
equity you own or does it just rent out
your time? So you can see it was great
that we brought in Naval for this
specific type of roast room. And
obviously last time you guys saw the PDF
that it creates, which is pretty high
level, but all of this stuff is stored
locally and you're able to dig in. You
can ask more questions about it. You can
inspect all that stuff if you want to
look at the debate more deeply. So it's
not lost data, of course. Show me where
all of the debates are held later if I
want to be able to dig in and ask more
questions about it. So as they're going
through round one and writing their
opening positions, I can just show you
real quick. If I go to the files and I
go down here to projects and then we
scroll down to a project called founder
council right here you can see that
there is different sessions in here and
these sessions will show us different
roast rooms that we've run since
creating this visual interface and we're
able to actually then dig in. And so if
I look at this one, we can see that
there was a brief, there was a round
one, round two, and a verdict. And this
will hold all of the session logs from
each of these people because as they
start to write their positions, we'll
see that all of their reasoning comes
through even when they start to debate.
And we can view it right in this
interface as well. So now you can see
they're starting to come through with
their opening positions. And we'll see
below their name what they voted for. So
Gary came in with voting for A and gave
it an 8 out of 10 score. Gino did the
same. And you can see A is Salt Lake
City and B San Francisco, Austin,
Chicago. This one, Alex Heroszi, also
voted for Salt Lake City. So, everyone
voted for Salt Lake City except for it
looks like Naval went for B, San
Francisco. And then, like I said, we
could click in and we could look at
exactly why. We could see the risk. We
could see what they would do. And then
we can keep seeing what everyone's going
to do. And now, what's going to happen
is they're going to read each other's
positions. And then they'll start to go
after each other and try to poke holes
in each other's opinions. In this case,
they all are in pretty much good
agreement, which is nice. But if they
did all completely agree, then the chair
or sort of like Claude code, the
facilitator of this debate, would make
one of them argue for a different side.
So they kind of play devil's advocate
and we get to see more perspective as
well. But in this case, we didn't have a
unanimous decision. So the debate will
continue as expected. Now, what I think
is really fun about this is we're able
to leverage the subject matter expertise
of other people. And humans are really
good at their domains, right? So like
for example, I could not build a
world-class copywriting agent. It would
be tough for me because I don't have a
copywriting background. But what I could
do is go find someone who I think is the
best copywriter in the world. I could
extract their frameworks, examples of
their copy, how they think, how they
decide what to write, and then I could
put them into this council. And when I
have questions about copy or, you know,
how to market something, I could
leverage them inside of this roast room.
And it doesn't mean it's going to be
perfect, right? It doesn't mean that
whatever this roast room decides, I
blindly take and accept. But just
getting in this mindset of thinking
about who has done something that you
want to do, who has done something and
proven it. Now, how can you go out there
and study what they did and how they got
there and basically just try to follow
that path? I think it's a lot better to
do that than just trusting Claude's gut
or trusting your gut sometimes. Like
following someone that's actually walked
the path you want to walk is a pretty
good signal, right? So doing these
councils helps me just look at things
through different perspectives and you
know think about things that I might not
have thought about because Paul Graham
brought up this idea or because Naval
brought up that idea. And so even
outside of the bounds of this roast room
for example, I think that just thinking
like that when you're building out other
skills or you're trying to automate
different processes, I think thinking
like that is a really good way to think.
But anyways, you can see they're
actually coming through now. They're
deciding on final votes and you can see
that we're probably going to win, you
know, Salt Lake City. It's 7.9 out of 10
right now. And that is probably the
verdict that we're going to get. But of
course, we could go through and we could
read everyone's key points. As you can
see, here is Hermosy's key point. Here's
Wickman's key point. You can see here
Bezos conceded to Gary Vee and Graham
about them being right on certain
things, but also disagreed the most with
Naval. So, anyways, that's how you could
sort of start to read through some
things in more depth. We can see that we
have the PDF now, which I'll go ahead
and download real quick. And now we're
able to look at the fact that Salt Lake
City won, which is actually pretty cool
because that is where we decided to have
this first inerson event. Now, anyways,
that is done. We could obviously do more
rounds if we wanted to. We could bring
in other council members. And now going
back to check on Elon, you can see that
it created the actual portrait for him
and it created these different views so
that we can see what it will look like
when he's actually talking. And then if
I go to the repo, we can see that we now
have Elon added in here. If I go to the
brain or not the brain, the agents, we
can see right here we have Musk. And
then of course in the actual brain
because it's supposed to do that through
the new roster skill, we have a brain
for Musk. Once again, it has hot books,
frameworks, positions, principles,
sources, stories, and a voice.md. So we
are now set up and we are able to use
Elon Musk inside of this roam council.
If you guys want to grab this GitHub
repo and play around with it, then just
go to my free school community. This
will be linked in the description. go to
the classroom and then grab it and from
the AI skills or from the all YouTube
resources, all of my other free GitHub
repos, skills, prompts, guides,
everything is in the free school
community. So anyways guys, that is
going to do it for this one. I hope that
you enjoyed you learned something new.
And if you did, please give it a like.
It helps me out a ton. And as always, I
appreciate you guys making it to the end
of the video, and I'll see you on the
next one. Thanks everyone.
