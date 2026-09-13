All right, so Marge, by the end of
today's episode, what will everyone have
learned from you?
&gt;&gt; My goal is that by the end of this
video, you understand that the harness
of a model is much more important than
the model itself.
&gt;&gt; It feels to me like Claude Code is like
a wise old owl and then it feels like
Codex is like the Rottweiler. It'll obey
your commands and it will just keep
going until it's it's done. Because
whenever we talk about, oh, Claude's
better or Codex is better, you have this
brain they're all fighting about, but
everything around the brain is actually
what gets it to tick. This stuff isn't
like magic at all. There is a whole
factory of workers that are making this
model look way smarter than it is. My
number one goal is to never be loyal to
a provider only be loyal to my harness
and my assets and I will switch the
brain interchangeably.
&gt;&gt; So I think that is really important to
be thinking you're building up your own
IP and you need to make sure that you're
protecting that. And I always think of
the quote you can outsource the thinking
but you can never outsource the
understanding. Skills and agents though
decay incredibly fast to the point where
Boris Churnney dropped a tweet saying
you should delete all of your skills
every six months. All of them.
&gt;&gt; Did he?
&gt;&gt; Do you know why?
&gt;&gt; Why did he say that?
&gt;&gt; All right. So, Mark, thank you so much
for joining us today in person, which is
awesome. We're in the beautiful country
of Montenegro, which has been so much
fun. We're here for an AI event and we
figured why not sit down together and
hopefully drop some sauce today. So, I'm
super super pumped to be sitting down.
If you guys don't know who Mark is, then
hopefully after this video you start
seeing his videos on your YouTube feed
because his stuff is absolutely gold.
I've been watching him for a while. I
actually was watching him before I
started making content. So, pretty cool
moment for me to be able to sit down
with Mr. Cashf here today. But, yeah,
I'm super excited to dig in. been
getting obviously tons of questions in
the community and discussion around oh
like we should be should we be using
Hermes now or we've seen this local
thing called PI and there's just so many
tools going around and I think we want
to make sure that what we're building at
the end of the day is still relevant
next year and the year after that
because we don't know what might happen
to cloud code next or codec so excited
to dig in and um yeah thanks for kind of
throwing together an excell let's let's
start getting into it
&gt;&gt; absolutely so so the first thing I want
to do is just really lock in on this
diagram specifically this little brain
in a jar are here because whenever we
talk about oh claude's better or codeex
is better or gemini maybe one date might
be better you have this brain they're
all fighting about but everything around
the brain is actually what gets it to
tick so if we look at the different
parts here so we have the ability to
read we have the ability to write and
edit files we have the ability to use
what's called bash which basically takes
control of your computer makes folders
moves folders all of these things aren't
baked into the model and you see this if
you ever use a local model and you say
make me a website and spin it up on my
local computer. It can do the first part
but it can't do the second part.
&gt;&gt; It is a brain that can tell you it can
give you this output of the HTML but it
can't go and spin up a local server on
your computer. It doesn't have the limbs
for that. So the more you start thinking
about models in the sense that they are
the brain but everything around them
allows them to interact and have hands
and legs then you start to really
separate what is the importance of the
brain versus everything around it and
how can you enrich everything around it
so you're less dependent on that brain
&gt;&gt; because we are at a point where many
local models whether it's a Kimmy or
insert name of open source model here
&gt;&gt; they can do like 80% of the day-to-day
work
&gt;&gt; you might not get the same firepower as
you would with cloud code or codeex But
for more and more roles increasingly for
the next year especially I see a world
where you run 70 to 80% on local
assuming you have the hardware and you
bring in the geniuses for genius level
tasks are planning.
&gt;&gt; Mhm.
&gt;&gt; I love that because I think when you
start to really talk about cloud chat in
the web
&gt;&gt; versus a cloud code
&gt;&gt; there is a gap there which honestly I
wish they didn't call it cloud code.
&gt;&gt; Yeah. Because the code part is all of
these these tools that you mentioned and
so like just to walk us through a really
practical example. What is the
difference between you asking claude
chat to let's just say research
something for you and create a PDF
versus when you might ask cla code to do
that exact same task?
&gt;&gt; Yeah. So claude on the web versus cloud
code on Yeah. So cloud on the web will
have slightly different tools. So let's
say you're using cloud chat and all it
can really do is do the researching
part, create the PDF part, but some
parts in between maybe calling
additional uh platforms or moving files
on your computer might it might not have
access to local files on your computer.
It would have to do a lot of work
assuming things in the background that
it can't actually touch and feel and
see.
&gt;&gt; With the cloud code as a harness, it can
not only interact with your local
computer, it can interact with the
cloud. So you have the best of both
worlds. So you have one that is telling
you hypothetically here's what we could
do and it could can do some stuff
increasingly it's getting better. I see
a world where claude chat evaporates
completely and all we have is co-work
which is a light version of the harness
of cloud code.
&gt;&gt; So everything we will interact with will
have a harness. It's just to what extent
is it highly capable to do the task
you're looking for?
&gt;&gt; 100%. And what I think is so cool about
cloud code and you know when I started
learning about it I remember how
intimidated I was to start learning
about it back in maybe January of like
this year
&gt;&gt; but when I just started asking it
questions it feels like magic because
yes you're interacting with the same
model you might be used to but all of
the harness stuff really just happens
automatically because the harness is
essentially built to understand here are
the tools that I have as you can see in
this diagram which well done on this
diagram by the way it knows what's in
there same way like you think
&gt;&gt; you need you pick up a glass of water,
your hands and your shoulder and it just
works together to do it for you. So, I
think that it's really cool to see
something like this and even though it
might at a glance look like you might
have to know how to do the bash or the
read or whatever.
&gt;&gt; Yeah.
&gt;&gt; But the model just takes care of it.
&gt;&gt; Yeah. And what I want to focus on is
although these come out of the box,
right, that's the whole point of the
cloth code harness. That's what made it
amazing is you have the read, you have
the edit, all the stuff is done for you.
And even with things like Pi, which is
kind of like a very vanilla open- source
version where you can build your own
harness, that's all cool, but where you
come in and where your channel has been
really adding tons of value is what else
can you add to this factory? So now you
have things like Lego blocks that are
modular and these are those skills,
these plugins, um all of these
additional things you can layer on. So
then you have this ecosystem, we have
this orchestra where you have the brain
in the middle telling everything else
exactly what the goal is. And depending
on the intelligence of the model, it
might become better at knowing ah for
this I need some bash with a write and
I'll need to go through what's called
the agentic loop which is purely you ask
thing thing gets executed result of
thing happens the result could be an
error it could be a success it takes
that stimuli and it keeps going in that
loop and its ability to keep going in
that loop comma well is fully based on
how sophisticated that harness is a
better model will know how to use tools
better. It's kind of like bringing an
expert handy person who's worked for a
year and studied for many ages versus
someone who has all the battle scars,
the really powerful types of tools and
has a tasset knowledge of when and where
to use them a little bit better.
&gt;&gt; They'll perform infinitely more
powerfully than the first one.
&gt;&gt; So the same concept here, both are going
to be smart. So the model itself is
great, but if I showed you right now an
example,
&gt;&gt; can we pop over to let's say an LM
studio? So let's pop over here.
&gt;&gt; Yeah. So what is LM Studio to anyone
that's never used it before?
&gt;&gt; Yeah. So think of LM Studio as your
ability to run chat GPT with an open-
source model. It doesn't have a harness
by default. So you can just interact
with the brain, which is beautiful
because it'll show you exactly why we
have an issue here.
&gt;&gt; Mhm.
&gt;&gt; So if I go and I'm just using Quen 27B
here. I have some more powerful models,
but I don't want this computer to
explode while I'm recording it.
&gt;&gt; So I'm just going to say using the
beautiful Glido.
&gt;&gt; Okay. So, I want you to make a very
basic landing page for my AI
consultancy. I want you to call it
prompt advisors and I want you to spin
it up locally on my computer so I can
host it and show the entire audience.
Now, if I run this over, no matter how
much time this takes, it will be able to
tell me that it can't spin it up. The
reason why is it does not have the limb
of being able to interact with my
computer to even create that server.
&gt;&gt; Mhm.
&gt;&gt; You get this exact same request to
codeex or cloud code. It's not going to
sweat even twice because it comes with
that out of the box. So now it's going
to create what is the HTML itself
because all it can do is take input and
get output. Imagine if your brain was in
a jar. All you can get is some form of
stimuli and release the signal of like
what you think the answer would be. Same
concept. So one can theoretically do the
thing,
&gt;&gt; but it can't take it from a all the way
to the touchdown.
&gt;&gt; Yeah. The whole point of the harness is
how do we go from the output of this
very intelligent model to some form of
tangible output in your hands.
&gt;&gt; Totally. Yeah. And I I actually remember
hearing some stories when you know
Claude first started to come around
first started to come around before we
had the harnesses and you would hear
these stories of these companies that
were building products because they were
having Claude write code and then just
copying and pasting it into whatever
they needed to actually build the code
and host it and all that kind of thing.
And that just it's another one of the
examples that goes right along with like
this is still inherently very powerful
but not as powerful as when you kind of
give it the whole agentic loop that you
talked about earlier. All right guys,
real quick. Huge thanks to Clay for
sponsoring this part of the video. Now,
one of the most common questions I get
is where to actually find leads for cold
outreach and how to learn enough about
these people to send them something that
they'll actually open because a raw list
of names doesn't tell you things like if
they have decision-making authority and
how to reach them or what they even care
about. So, Clay is a data enrichment and
orchestration platform. And it gives you
access to over 250 data providers and AI
research tools all in one spot. So,
instead of asking your agent to dig up
whatever it can find online, you can
research a whole list at once and pull
the right person to contact their work
email and the size of their company. And
if one provider comes back empty, Clay
just moves down the list to the next one
until it gets you a result. And what's
really cool is the logic you build stays
attached to your data. So the same steps
can be run again and again on every new
lead that you add. And you can see each
step that it took, like which provider
every value came from and what it cost
you. You can build all of this from
Cloud Code with the Clay CLI, which is
what I'm doing right here. So try Clay
using the link in the description, and
you'll get 2,000 free credits. Now,
let's get back to the video. Okay, so we
talked about how important these pieces
are because this is where you can really
start to add in your own like subject
matter expertise,
&gt;&gt; which is really what helps make the
system feel more like it's yours. And
what's cool about this stuff is that as
you build on like maybe these skills,
context files, plugins, whatever it may
be, you're not locking yourself in to
that harness because these can be used
across other harnesses and other models
as well.
&gt;&gt; So the question I wanted to ask you is
as you switch through these things and
you know your codecs can touch your
AIOS, your second brain, whatever
everyone's calling it these days,
Hermes, openclaw, whatever comes next.
How do you personally, Mark Cashup, how
do you think about the way that you
switch between those harnesses and like
you know if you like codecs for certain
tasks, Hermes for certain tasks, what
does that look like for you?
&gt;&gt; For sure. So my number one goal is to
never be loyal to a provider to only be
loyal to my harness and my assets and I
will switch the brain
&gt;&gt; interchangeably. I have zero loyalty to
that.
&gt;&gt; So although I use cloud code a lot, it's
more so I'm used to it. I know the
rhythm of it. I know what to expect.
Mhm.
&gt;&gt; But I will create all of my skills so
they can work with any language model
open to closed source
&gt;&gt; and I will prioritize really battle
testing it with every single thing that
I can. So I'll try with cloud code. Then
I have the skill I call / poly skill.
It'll convert any skill for cloud code
and optimize it for codeex.
&gt;&gt; Okay.
&gt;&gt; So I'll make sure that every skill is
eligible for both.
&gt;&gt; That both all of the different models
know exactly where to find the same
assets. So I have one link that has all
of my core assets. They're agnostic of
working with any of those models. So I
can move around as needed.
&gt;&gt; Yeah.
&gt;&gt; Now with your question, codeex recently
I've been running 60% of the time.
Although I've been very loyal loyal to
Claude Code for the vast amount of time.
Claude Code is amazing at ideiation and
planning to an extent. It's a visionary.
&gt;&gt; It likes to go back and forth. It likes
to judge you. But the one thing it
doesn't like to do sometimes is follow
the exact instruction in the exact way
you gave it.
&gt;&gt; So I see Codeex as a surgeon and Claude
Code as a gifted artist.
&gt;&gt; Yeah.
&gt;&gt; And many times I have to bring in Codeex
to look over the plan of Claude Code and
I make them fight in a loop for 10
different rounds until Claude Code
finally has all the missing parts that
Codex could see. All the things it
wasn't anticipating.
&gt;&gt; Totally. Yeah. I heard this tweet that
or I saw this tweet that I thought was
awesome and I want to see if you agree
and I think you will because I have a
very very similar philosophy to the way
I I think about the two. But it
basically said like it feels to me like
cloud code is like a wise old owl. You
can talk to it, you plan with it, it'll,
you know, push back on you a little bit
and then it feels like Codeex is like
the Rottweiler that will grab onto the
task and it will just it'll obey your
commands and it will just keep going
until it's it's done essentially because
I think that the the verification loops
inside Codex feel really really sharp to
me. But um I think it's important that
we kind of have that acknowledgement of
you know which harness is best, which
model is best. And it's it's more so
which one is best for this specific
task. Yeah, it might be, you know, a
fivestep process, but for step one and
two, maybe that's where you go for the
codeex and then, you know, or vice
versa. So, I think that's that's good to
hear you say as well. Now, where do you
see
&gt;&gt; um you know, I think that Hermes and
Open Cloud kind of get bucketed in
together as well. Where do you see the
differentiation there and you know with
COD and cloud code as well?
&gt;&gt; Well, with Hermes, what are you doing?
You are bringing in the Hermes harness
&gt;&gt; and you're just looping in whatever
whatever model you want. So the reason
why people have to really make their
Hermes agent tailored to them, a special
snowflake, is depending on how they want
to use these models with Hermes, they
have to keep hacking Hermes harness. Not
this all these skill MD files, etc.
They're all great, but the thing that
made Hermes better than Open Claw is its
harness. So with many tasks if you go
one to one Hermes agent versus codeex
you'll have a different result vanilla
but you can eventually massage Hermes
agents harness
&gt;&gt; to do this verification loop that you
mentioned earlier they really like about
codeex is that it performs a very
similar to it so you can do a level of
monkey see monkey do.
&gt;&gt; Yeah.
&gt;&gt; So one thing that I did and you know you
can go obviously no affiliation here
it's open source. If you go to pi.dev
dev, you will have this harness that you
can bring onto your computer. You can
copy with one command or if you're
feeling daunted, what I did is I take
this link, I feed it to codeex or cloud
code and say go read the documentation,
fan out some agents, learn about this
whole harness thing. Once I do that, I
can then ask it to go through what are
called JSON L files. Basically, every
conversation you have on your codeex and
cloud code exists on your computer. So,
I'll have it go look through all the
conversations because they have the
metadata of what tools were called, what
verifications were done, in what order,
and then I could have it monkey see
monkey do. How do I start to make my own
version of the harness that would react
and do the same things based on similar
types of tasks?
&gt;&gt; You can start to reverse engineer all of
the things that you love about cloud
code and codecs. bring it to your own
harness and eventually you can have one
harness for everything where you bring
in all these models as a brain that's
leased you swap out as you need. So
that's where I think we will get to
where right now everything's tribal
right YouTube is tribal X is tribal I am
team CEX I am team cloud code I am team
open source you all are Neanderthalss
right for me I'm anti- tribal I am how
do I make a system where any brain that
could serve me for the best speed for
the best rate at the best time can be
swapped in with little to no acclimation
needed
&gt;&gt; so it's not a pain for me if Gemini
wakes up tomorrow
&gt;&gt; truly wakes up and now it becomes
amazing saying, "Okay, it could probably
take me 24 hours to swap everything to
Gemini."
&gt;&gt; Mhm.
&gt;&gt; And I love that nimleness.
&gt;&gt; Yeah.
&gt;&gt; Because while Codeex is amazing today,
Cloud Code might come cuz they're
probably going to IPO sooner. Make a big
push. And if we finally get a mythos
that's not nerfed or neutered to
infinity,
&gt;&gt; you might want to move all your stuff
there.
&gt;&gt; Yeah. Yeah. And who knows what could
happen from a price perspective as well
for us as consumers. So I think that is
really important to be thinking you're
building out your own IP essentially and
you need to make sure that you're
protecting that and it's it's nimble. So
I love that point there.
&gt;&gt; Now you mentioned something earlier
about making sure that your skills and
your whole ecosystem is model agnostic
and you have a special skill that you
use to make sure that they can work and
are optimized for different models and
harnesses as well.
&gt;&gt; What does that actual process look like?
Because typically when we see like our
skill files or folders, it's usually a
markdown file and that's sometimes assoc
or you know kind of like also has in
there maybe a few Python scripts or
whatever the skill does. Maybe there's
some assets that go along with it but
ultimately you've kind of got just like
a master markdown file. So how do you
actually make sure that codecs can pick
it up and use it as well or other agents
could pick it up?
&gt;&gt; Absolutely. So the main thing to
remember is that like you said all these
skill files structurally look similar.
They have this thing at the top called
YAML where it's the name of the skill
and what's called kebab case. You have
the description and in the description
you have a series of trigger words where
when user does X I want you to invoke
the skill to do Y.
&gt;&gt; So what I did is I offload this. I asked
codeex go and take a look at all the
documentation from cloud code. Look at
your own documentation. look at the
documentation from let's say this
specific other provider and go see how
to build a versatile Swiss knife skill
that will work for all of them as
optimized as possible.
&gt;&gt; Mhm.
&gt;&gt; So Codeex prioritizes some things about
skills that cloud code doesn't and vice
versa. So how do we make sure that both
are included? Now when it comes to
scripts, Python is Python luckily. So
that is already generic on its own. No
need to worry about that. how you invoke
that Python, how it knows when to use it
and how to use it. That's where you
might need to massage it a little bit.
&gt;&gt; So even when I use this / poly skill, it
will always look for these slight
differences knowing ah codeex might miss
this in the way that you're triggering
it using cloud code. So let's make the
description that much more beefier.
&gt;&gt; So the likelihood that it picks it up
across the board is much higher.
&gt;&gt; Totally. So I just have AI do the dirty
work to go see AI documentation and I
update these monthly on a cron job. So
every month
&gt;&gt; I will auto audit audit my entire
ecosystem
&gt;&gt; refine all my skills see where I'm not
using skills that I've added because a
lot of people your audience and mine
have bloated skill repositories where
they downloaded some awesome skills
thing they have 300 of them they load
every single time and they use five.
&gt;&gt; So it reduces the number of skills that
I have. It combines the ones where
there's an opportunity for a compound
skill and then it makes sure that
they're all model agnostic. I love that.
Yeah. I think what's really important
there is, you know, what you said, you
have AI do the dirty work, but you are
still very much in control and you still
understand. And I always think of the
quote, you can outsource the thinking,
but you can never outsource the
understanding. Mhm.
&gt;&gt; And I think it's a great mindset shift
to realize that
even us as creators, a lot of the things
that we don't know or that we need to
learn, we have AI help us with it, but
we still understand
how to feed in like the documentation
for it to look through and we understand
now that it has this knowledge what to
do with it. And I always kind of say
this in my videos even though it might
like hurt the views. Sure.
&gt;&gt; Is that ultimately like just use it as
your your thought partner as long as
you're not outsourcing everything. I
think that's a really important way to
think about how you
&gt;&gt; as a person continue to learn more too
as well.
&gt;&gt; Absolutely. And one thing you can do is
again if we move into this world of you
owning your own harness, you can have
the same task be executed and then cla
can watch it and it can run it within
the terminal on your PI harness, run it
on the other model providers, observe
exactly what happened and what was the
end result and try to continually
understand and reverse engineer what
happened with the others that's not
happening with yours.
&gt;&gt; Mhm. Back in March of 26, we had the
cloud code harness leak. If you remember
that, it was a map file. It was leaked
to the whole world.
&gt;&gt; I spent four to five days, and I I'm
pretty sure you went and made a couple
videos as well,
&gt;&gt; looking through every single piece of
it. Mhm.
&gt;&gt; And the coolest part was the majority of
the harness was full of all these
crutches they gave to the brain, the
model to not swear at the user to detect
when you had swear words
&gt;&gt; through a list of regex of all the swear
words you would have that would tell the
brain how to react. So once I saw there
were so many crutches for this
supposedly AGI level model, it made me
wake up. Ah, this stuff isn't like ma
troop magic at all. there is a whole
factory of workers that are making this
model look way smarter than it is.
&gt;&gt; And as soon as you understand that one
concept, that's when you snap out of it
and you start looking at model
benchmarks very differently, you are not
as wowed by what bench it crushed.
You're more wowed by how well the model
provider do in now improving their
harness to have a symbiotic relationship
with this brand new model's brain.
That's how that's why I care about
empirical. How well does this do when I
push it versus how well are they telling
me it should perform based on how smart
it is?
&gt;&gt; Absolutely. There there's a question I
wanted to ask you that I get a ton and
um it it it revolves around this whole
harness idea. It revolves specifically
around this idea of
&gt;&gt; building out your own second brain or
OS. Mhm.
&gt;&gt; The question that I get a lot is about
as you every month are adding in new
things, whether that be skills or um you
know an LM wiki, how do you yourself
make sure that it's staying optimized?
And I put that in air quotes because I
don't I truly don't believe that there's
only one optimal way to do it. I think
it's just a matter of making sure that
you can feel when it's maybe searching
too long for something that it should
find right away or it's hallucinating
information because of the bloat in a
certain folder. So I would love to hear
just kind of like dive into your brain a
little bit.
&gt;&gt; How do you think about keeping that
organized and
&gt;&gt; efficient? Sure.
&gt;&gt; So the biggest thing that I've done is
create what's called a rot.md
file.
&gt;&gt; Okay.
&gt;&gt; Rot meaning decay. So if you have
different layers of an AIOS and you have
entire courses on this, you you covered
this at length. You have five to six
layers. One could be your identity, then
your substrate, which is your core
context that shouldn't change that much.
Then you have your skills, your rules,
your hooks, you have your agents, and
then you have additional things you can
add on. All of these different parts
decay, become obsolete or rot at
different rates. Mhm.
&gt;&gt; So who you are, what you do, your goals,
your aspirations unlikely to change very
quickly.
&gt;&gt; So you could have 1 to 3 months maybe
even maybe longer if it's a company
actually using this where it's relevant.
&gt;&gt; Skills like I said I optimate up I
update and optimize on a monthly basis.
I just made a brand new one.
&gt;&gt; I like the word actually.
&gt;&gt; And then you have let's say your rules.
&gt;&gt; Your rules can change daily. I have
rules that change daily because as I do
new tasks with the same AIOS, I find new
limitations and new edge cases.
&gt;&gt; So I find ways to refine and make better
skills that are more compound.
&gt;&gt; My rules probably decay every week.
&gt;&gt; Yeah.
&gt;&gt; My hooks though, so things that it
always checks. So if I push a client
project to GitHub, it wants to make sure
that there's a hook that fires to remove
any PII, any sensitive data of that
client that I don't want living on my
GitHub.
&gt;&gt; Mhm.
&gt;&gt; That that might not decay for 6 months.
I might change it a little bit, but it
won't really be viable to be decaying at
a very high rate. Skills and agents
though decay incredibly fast to the
point where Boris Churnney dropped a
tweet saying you should delete all of
your skills every 6 months. All of them.
&gt;&gt; Did he?
&gt;&gt; Do you know why?
&gt;&gt; Why did he say that? Because a skill is
basically an e extra crutch that we're
adding to the system to help the brain
do things or the brain better understand
how to use all these tools to do the
thing. But if the model truly gets way
smarter, it might not need the skill to
shortcut what tools to use at disposal.
It might be able to accomplish the goal
of the skill with purely a vague prompt
versus the vague prompt plus the skill
&gt;&gt; that's injected every single time. So
you want to make sure that your skill is
actually adding value and not holding
back this dragon that gets only bigger
with time and smarter with time and more
powerful. So skills is one thing you
want to audit very aggressively because
you might not have a skill issue with
that thing you built it for 3 months
down the line, 6 months down the line
with things like let's say agents. You
hire agents like you hire employees. You
might not always need a bookkeeping
agent because if the model gets good
enough, you might be able to give vague
prompt. It would know exactly what are
the 18 to 20 different subtasks based on
all the memory assuming your memory gets
better that it needs to execute.
&gt;&gt; So we could live in a world where you
have a handful of skills, a handful of
rules, and those skills are actually
very specific task at knowledge that it
would never know no matter how smart it
was versus step-by-step instructions.
Wow. Yeah, that is really interesting.
You know, I always make it a point to
every time a new model comes out and I
have, you know, I've got the new Opus
model or whatever plugged into Cloud
Code, I always make it a point to have
that model run through all my skills
just to make sure that it can use them
in the same way and and things like
that. But I have never thought really
to, you know, I hadn't seen that tweet.
I had I hadn't thought to go back to
some of the like through all of them and
say like, do we even need this? And what
happens if you try to run that process
without the skill?
&gt;&gt; Exactly. So
&gt;&gt; given your meteoric rise on YouTube, if
I told you, hey Nate, here's how you
make a YouTube video, right? Two years
ago, this might have been a helpful
skill for you to learn from me before I
I started before you. But now I gave you
that same play. You'd look at me, tilt
your head, and be like, have you looked
at our subscriber counts?
&gt;&gt; Right? You don't need this skill
anymore. You have outgrown this skill.
&gt;&gt; That's really interesting. So as a model
becomes very diverse and has training
data, you might not need the skill
anymore. It might not it might be
obsolete for where the model's at.
&gt;&gt; Have you had an example yourself where
you've been able to remove a skill
because the model and the artist now
just can crush it out of the water?
&gt;&gt; Basically now if I tell it go and read
all the conversations that we've had and
tell me 15 different things we can
optimize. Mhm.
&gt;&gt; I used to have a skill that would tell
exactly where to look for the files that
are associated with our conversations,
how to break it down so it doesn't blow
its context window with 50,000 tokens at
once times 100.
&gt;&gt; I used to have to really explain that
bit by bit.
&gt;&gt; And now I went from skill to now we're
moving to skill and now I have one basic
sentence and it knows exactly to
optimize based on my cloud. I'm always
trying to optimize my uh context window
and my context use. it on its own can do
that without me telling it to.
&gt;&gt; That, you know, that makes me think of
something that's that's really
interesting because of that ability for
it to be more creative and arguably a
better problem solver because it knows
how to get to that end goal. Mhm.
&gt;&gt; That might also be kind of a scary thing
because in some cases maybe the skill
keeps it on stricter guard rails
&gt;&gt; potentially
&gt;&gt; because sometimes now if it has to try
to find its own way to from point A to
point B, it might try to create some
things that could potentially be harmful
to the system or something like that as
well.
&gt;&gt; But that's where the rest of the AIOS
comes in because like the AIOS is not
just a skill. You have the rules, you
have different layers to babysit.
&gt;&gt; So we might live in a world where we we
need way less skills and much stricter
rules. And your cloud MD now just
basically says go and follow these rules
for these kind of situations
&gt;&gt; and that could be sufficient enough.
&gt;&gt; Yeah.
&gt;&gt; So some of these layers, even the
concept of assigning an agent and
creating your own agent that's all spun
up the same way every time, that could
become obsolete. So, I'm not saying it
is, but I'm saying we should be
open-minded that this stuff will evolve
and as long as you keep your core assets
nimble, then you should be good to go. I
love that. You know, I did see which I
thought was really interesting. I don't
remember if it was Opus 5 or Fable 5,
but one of those drops
&gt;&gt; from Enthropic, you know, how they
dropped the blog with benchmarks and
just like how to use it, how to prompt
it.
One of the things I remember being at
the top was
give it more ambitious tasks. And you
might just skim through that, right? But
to me, that made me think, well, why do
they feel the need to put that in there?
Maybe they feel like people aren't
pushing the models to their true limits
and getting out of the model's way. And
that's when I started to run these just
interesting experiments. I'd set a SL
goal and I'd say like kind of something
along the lines of like impress me like
build me build me this but impress me
and show me what you can really do. And
I just thought that that was interesting
that they put that in there and it just
shows like that kind of makes me think
that whole skill thing like the skill
that we we maybe have baked in a long
time ago and now we just kind of blindly
use because it it works. we are almost
yeah kind of
baking in or or limiting what the model
could truly do because it's it's kind of
going down these these guardrails. So I
think that's that's really interesting.
You know, as we sort of start to wrap up
here today, I'd be interested to hear
from from you. What is something that
you think that you do within your
cloud code or your harness setup that
most people don't do and that you think
is important that everyone should be
doing?
&gt;&gt; So the main thing I think about is many
times I have let's say 25 different
operating systems.
&gt;&gt; So some people like to create one big
one.
&gt;&gt; I create very specific ones that live in
an isolated world.
&gt;&gt; Okay. So my tax and finance lives very
differently from my consulting OS which
is very living very differently from my
school OS for content for there versus
everything else.
&gt;&gt; So me segmenting every single part of my
business my education offers everything
we do for enterprise clients each thing
has its own set of operating systems.
&gt;&gt; It's more to upkeep for sure but as you
build more you start to build more
leverage. So I have one mega system that
depending on its audit of every single
operating system I have will come up
with a series of things that we need to
make that specific thing better that
specific operating system work better
and one that generalizes across all of
them.
&gt;&gt; So as you create different folders
you'll have some project level skills
rules cloud and then global. Mhm.
&gt;&gt; Some people make everything global,
which is awful because as you add new
things, you might notice under
performance cuz you forgot that you have
this global spectre of rules applying to
every single thing.
&gt;&gt; So for me, I have a different concept
where I think about promotion.
&gt;&gt; Everything is project until deserves to
be promoted to global so that I know at
all times what is the running total of
everything that's running globally.
&gt;&gt; And I have a very few number of things
that are global. Everything's project
specific. But that also gives me this
the flexibility to have a very small
blast radius if I want to be
experimental. If I want to audit and
push a certain folder for a certain type
of task and not have that bleed over to
another project and not know why is this
not working, is the model worse? Is the
harness worse? Or is my setup worse? So
because I'm so meticulous about is this
a model problem, is this a harness
problem? Or is this an organization
problem? when I can isolate things, I
can find the issue faster.
&gt;&gt; So, Fable is amazing with my tax, but
all of a sudden, it is horrific with my
consulting operating system.
&gt;&gt; It might not be a model issue.
&gt;&gt; It might not be a skill issue. It could
be an organization issue for that model
that I might have to adhere to for this
specific project.
&gt;&gt; And that helps me control bloat and find
the area of resistance that I need to
move to actually get the reforms I'm
looking for. I think that's really
smart. I think especially because these
things are so so autonomous and agentic.
&gt;&gt; You have to be able to
find the actual variable that that
killed the thing. Otherwise, there is no
learning there and there's no
improvement there.
&gt;&gt; And it it it for the most part you can
help like it can help you find out why
it went wrong and where. But I think
that level of isolation and I think the
key is there that you know how your
different folders are drilled down. Yes,
&gt;&gt; you know, you're not just blindly
trusting that it can find everything.
You still intuitively
&gt;&gt; I have a feeling that if you are looking
for a specific deliverable, you could
find it just by clicking through your
files and folders because you kind of
know where the things live and you know
how to drill down.
&gt;&gt; Yes.
&gt;&gt; And I think that that's just highlights
the point again that you cannot
outsource your understanding. You still
have to understand where everything is
and how it works.
&gt;&gt; Yeah. The last thing I was going to say
is that this becomes an acquired skill.
And if you want to get to mastery,
mastery is just understanding how the
entire factory works end to end and
where each piece lies. So if you want
more leverage, if you're running into
issues where you're kind of being
intellectually lazy and saying, "Oh,
this model sucks." Before you pass fully
judgment on it, you want to make sure
that maybe it sucks, for the setup that
you currently have. So when in doubt,
audit your setup, audit your skills,
audit the bloat because different models
