Okay, so over the last 6 weeks,
Enthropic has shipped three new models,
put docs, slides, and designs inside
every single chat, launched dashboards,
and animated explainers, released a
brand new Asian app called Duet, and the
$200 plan doesn't even have a 5h hour
limit anymore. And people are kind of
calling this Claude 2.0, which is just
obviously a nickname, not a new model.
And if you feel a little bit lost right
now, that's probably pretty normal. So,
in this video, I'm going to break down
every claw concept that you need to
understand, 25 of them in plain English,
split across five parts, and you don't
need to be technical at all or know how
to code for any of it. So, let's get
right into it. Okay, so part one is the
brain, which is basically what Claude is
actually running on. And concept number
one is AI models. Cloud isn't just one
AI, it's a family of models. And right
now, there are three main models. Haiku
is the small one, so it's cheapest and
fastest. Sonnet is kind of the everyday
workhorse. And Opus is the one that you
hand the big long messy jobs to. And
right now they're all kind of called 5.5
because that's the most recent version.
But in the future we'll see six and we
will see 7 and 8. Now we also do have
another model that's even more
intelligent and it's called Fable. But
for right now you can say that the
majority of work even Opus is overkill.
So like Sonic 5.5, Opus 5.5, very very
good models. But the way I think about
them is like a team. You wouldn't have
your most senior person answering every
quick email, and you wouldn't hand the
whole project to your newest hire. Now,
I actually tested Sonnet against Opus on
seven real workflows, and Sonnet won the
stuff with really clear instructions,
like a resource guide where it could
finish it in about half the time, and
usually cheaper than Opus. But Opus won
the tasks when the goal was vague, like
building out a 90-day plan. And keep in
mind, on the free plan, you get Sonnet
and Haiku, but not Opus. Now, the other
one that I talked about, like I said,
Fable. Fable 5.1 is Enthropic's top tier
model. It's the one that the government
actually took away when they first
dropped Fable 5 because it was too
powerful. And they say that it's built
for demanding reasoning and really,
really long tasks where Claude works on
its own. And it's also very expensive.
If you pay per use, it costs two and a
half times what Opus does. And
Enthropic's own release notes say that
Opus 5.5 performs near fable level on
most work. So for most of our use cases,
Opus is going to be plenty of power.
Now, on max and ultra plans, which is
the subscriptions that you get on, you
know, 20 bucks a month, 100 bucks a
month, or 200 bucks a month, Fable can
use up to half of your weekly limit, and
on Pro, you pay for it with usage
credits. There's also a command
called/advisor that lets Claude check in
with a stronger model like Fable at key
moments during a task. So, you get some
of the brain power without running the
entire job on Fable. All right, so
concept number three now is tokens and
the context window. A token is basically
a chunk of word and it's how everything
gets measured for AI models. Both what
you pay and how fast you hit your
limits, whether that be the session
limits or the weekly limits. And then
the context window is how many tokens
Claude can hold in its head at one time.
Every current model inside of Cloud Code
has a 1 million token window, which
Enthropic says is roughly 555,000 words.
So like a whole stack of novels at once.
And most of your tokens go to reading,
not writing. When I measured seven of my
own tasks, Claude read about 160 million
tokens and only wrote about 800,000. So
for every token it writes, it might be
reading about 200, which is why the
stuff you load in, like your files and
your instructions, those matter so much
more than how long your prompt is. Okay.
Now, number four, effort levels. Effort
is how hard Claude has to think or how
hard Claude does think before it
answers. And the levels that you get to
choose from are low, medium, high, extra
high, and max. Now, on the 5.5 models,
the default is medium, and you can
change it by either typing /effort or by
in the bottom right in the desktop app,
just choosing the effort level. But more
effort isn't always better. I actually
ran an experiment where I gave Opus 5.5
the exact same prompt at every single
effort level. Low finished in about 17
minutes for under $4, and it was super
glitchy. Extra high was the winner at an
hour and a half of run, but it cost
about $26. And Max in this case took two
and a half hours, cost 50 bucks, and was
not really that good. It was still
buggy. So, Enthropic's own docs even say
that max is prone to overthinking. So,
you don't need to give it so much power.
So, what I do myself is I keep medium as
my everyday setting, and I only bump it
up for really hard stuff like video
editing. I'll always throw it on extra
high. But, if you're creating docs and
you're doing general knowledge work, you
could even just use Sonet 5.5 on medium
for most things, especially when you
combine that with skills, which we'll
talk about later. Now, there is also
something called Ultra Code, which isn't
really a level. It's more of a setting
where Claude plans out the whole
workflow for each big task before it
starts. So, that is something that you
can pull another lever as well. But
anyways, number five is about usage
limits and plans. So, Claude has two
limits running at the same time, a
5-hour session limit and a weekly limit,
and they are shared. So, your chats in
the Cloud app and your work in Cloud
Code all pull from that same bucket. So,
for plans, free is $0 a month. Pro is
$20 a month. Max is $100 for five times
Pros usage. And then the $200 plan is
now called Ultra. And Ultra gets you 10
times Pros weekly usage. And for
verified Ultra accounts, there's no
longer going to be a 5h hour limit,
which is pretty awesome. Max and Ultra
also come with $100 and $200 a month in
API credits as well, which are for
building your own apps on top of Claude,
so they don't work inside the Claude
Code app. It's more about like
programmatic automations that can sort
of like run more in the background. Now,
if you want to see where you're at, you
can just type / usage or you can click
on the little circle in the bottom right
of the desktop app. And a lot of what's
in this video depends on your plan. So,
if you watch a video and you don't see a
particular feature, then maybe it's
because of the plan you're on, or maybe
you need to be on a wait list or
something like that. And I put together
a free cheat sheet with all 25 of these
concepts and exactly which plan gets
what, and that is inside my free school
community, which is linked down in the
description. So, anyways, that's what
Claude runs on. But where do you
actually use it now that the app has
three different tabs? [music] So number
six is chat. Chat is the claude that
most people already know where you just
type a message and you get an answer
back. But since September 16th, chat can
do a lot more than just talk. You can
make docs, slides, and designs right
inside any conversation. And even the
free plan gets web search, memory,
connectors, and artifacts. And I'll
explain all those things in a little
bit. So chat is where you could go to,
you know, kind of do a Google search or
think things through really quickly or
make some quick drafts. But number seven
is code. So claude code. The code tab in
the desktop app is cloud code. And I
know the name scares a lot of people
off, but trust me, it's not scary at
all. Cloud code works inside a folder on
your computer. So, it can read your
local files. It can create new ones,
edit them, move them around. It can run
commands. So, it's less of a chatbot and
more of an assistant that actually does
the work. And it's not just for
developers. I promise you, I don't come
from a coding background. And pretty
much my entire business runs out of
cloud code out of one folder. Everyone
on my team, no one's a formal coder, but
everyone uses cloud code. And that's how
we're able to move so much faster. It's
literally like having a best friend that
is the world's best coder that talks to
you like a normal person and you can ask
it to do things like a normal person.
It's also how I edit all my videos like
the one that I'm you're watching right
now. I recorded it. I handed Claude the
footage and it helped me kind of cut out
things and get the B-roll and throw it
all together. Claude Code comes with pro
and up when we talk about subscriptions.
Now, number eight, co-work. Enthropic
literally describes co-work as claude
code for the rest of your work, meaning
all the stuff that isn't coding. You can
give it a goal. it can work across your
files and your tools and you can come
back to finished work that you can just
review. And their examples are things
like reviewing a whole folder of
contracts against a playbook or building
a spreadsheet that reconciles a bunch
of, you know, regional exports or
reports or something like that. But
honestly, the way I feel about it is why
learn if eventually you might need the
power of code. So, I would just
recommend that you're learning cloud
code and my channel has tons of great
videos. In fact, I'll tag a 6-hour cloud
code course for non-coders, for regular
people right up here so that you guys
can check that out after this video if
you need to. All right, so moving on to
number nine, sessions. Every
conversation in the cloud code tab is a
session with its own history and its own
folder. And Enthropic rebuilt the
desktop app around running a bunch of
sessions at the same time. So you can
have one session doing research, another
one writing, and another one building,
all side by side. It's super super
slick. You can also hit command N for a
new session. And you can open two of
them next to each other in split view.
Cloud can even message and manage your
other sessions for you. It's really
really cool. I've had days with 18 or 20
or 30 of these running in pairs just to
test models against each other. And I
actually built a little mod that warns
me when two sessions are about to edit
the same file. And with remote control,
your computer shows up on your phone so
you can check in on sessions from
literally anywhere if you have your
phone. Now, number 10 is side chats.
Let's say you're halfway through a big
task and you want to ask a question
without derailing that session. You can
hit command semicolon or you can type
/btw for slash by the way and you can
get a side chat and it can see
everything in your session but nothing
that you say there gets added back into
that main conversation which is super
nice. Just keep in mind here that in the
desktop app it doesn't save your side
chats. So if you close one from the app
it'll be gone. But that brings us on to
number 11 which is Claude Duet which is
Enthropic's brand new agent app. You
message it the way you'd message a
person by typing or talking and it does
things in the apps that you've connected
and it's super super proactive. It's
basically its enthropic's response to,
you know, Meta's Muse and OpenAI's dots.
But every morning, it can do things like
scan your email and your calendar. It
can flag what needs your attention, and
it can start drafting replies for you to
review right away. And throughout the
day, it follows up on threads that have
gone quiet. It's designed to ask you
before it sends a message or makes any
sort of payment or signs a document or
deletes anything. And right now, it's in
research preview with a wait list, US
only on Pro, Max, and Ultra plans. So,
that's part two. That's where you use
Claude. Now, let's talk about what it
can actually make for you. Okay, so
number 12 here is artifacts. [music] An
artifact is anything that Claude makes
for you that opens up right beside the
chat, like a document, a deck, a design,
a dashboard, or a small interactive
tool. Really, whatever you want it to
be. And they start out private, so
nobody sees them unless you actually
share them. And I actually made our
October all hands deck for my team as an
artifact. But I've also made like
internal apps and actual like dashboards
that I want to come back to and revisit.
I've made those artifacts as well. I've
even made myself an artifact when I was
planning a trip with my friends and I
could send it to them as well. So, very,
very cool stuff. Now, number 13 is kind
of like 13, 14, 15, but we're just going
to call it 13. And this is docs, slides,
and design, which are the three most
common types of artifact. So, docs are
documents, slides or presentations, and
design is for visual stuff like landing
pages, and you know, app mock-ups or
something like that. As of October 8th,
all three of these are out of beta and
on every single plan, including free.
And Enthropic says that people have
already made over 45 million docs,
decks, and designs. So clearly, people
are loving this feature. Now, I did do a
full 2-hour course on Cloud Design back
in April, and the big change since then
is that you don't have to go anywhere
else to use it. It used to be a separate
app, but now design lives right inside
your chats. And the old standalone site,
cloud.ai/design,
is going to be closing in December of
this year. So, if you've got a bunch of
workflows over there, just make sure
you're kind of like aware of that or
you're going to think that they have
disappeared. But anyways, that brings us
on to number 14, which is dashboards.
You ask a question about your business
in plain English, and Claude pulls the
answer from your data. It builds a
dashboard, and it keeps it updated as
the data changes. It connects to things
like Big Query, Snowflake, Data Bricks,
and Salesforce. And you can click on any
number to see the exact query behind it.
So, you're not just trusting a chart
that you can't check. Now, dashboards
right now are in beta on the paid plan.
So, if you don't see it, that's probably
why. But don't stress. Everything
eventually rolls out to everybody except
for Mythos. We still haven't gotten
that. But anyway, number 15 is motion.
Motion turns a prompt into a short
animated explainer that plays like a
video and then you can download it as an
MP4. So, it's basically clawed native
video editing. Now, I myself typically
use Hyperframes, which is a free open
source tool for video editing. But all
of this is getting really, really good.
And the key about this AI video editing
is that it's not using a video
generation model. The animation is
actually built with code. So, there's no
AI generated footage or fake people in
it. It's in beta right now on Team and
Enterprise right now, but like I said,
it will come out to everybody. And this
is pretty much the same idea that I use
for my own videos because a lot of the
motion graphics on my channel are built
with code with Claude Code as well,
which is why they're so easy to change
because I can change the color of
something or the size of something
without having to rerender the entire
like if it was an AI generated video. So
Claude can do a ton of stuff, but it's
only as good as what it knows about you,
which is part four. [music] So number 16
is memory. Every new conversation starts
completely fresh. Like when you shoot a
new message off to Claude, it basically
wakes up blind and it has to read things
in your project in order to know who you
are. And memory is how Claude carries
things over from one session to the next
or from one day to the next. Now, in the
Claude app, memory is on every single
plan, even free. And in Claude Code,
there's something called automemory
where Claude writes its own notes based
on your corrections and preferences, and
then it reads them at the start of every
session. So, literally, the more you use
Claude Code, the smarter it gets about
you and how you like to work. Now, I've
got over 150 of those notes right now
inside of my projects. One of them
literally just says that Grockbot is
spelled with a space because I corrected
it enough times because it kept spelling
Grockbot without a space. So, automemory
is in fact automatic. Now, number 17 is
the claw.md.
So, if memory is what Claude writes
down, claw.md is what you write down.
It's just a text file with your
instructions and your rules. And Claude
loads it at the start of every session.
So, mine basically starts with, "Hey,
you are Nate Herk's AI operating system.
your job is to save him time, blah blah
blah. And then it's basically just a map
of where everything in my business
lives. So if you want business contacts,
you go to this folder. If you want, you
know, brand assets, you go to this
folder. And it's just a a routing map of
where it can find all my stuff. Now, one
quick tip is that you want to keep this
lean because it loads every single time.
Remember how I said every time you shoot
off a message cloud, it wakes up fresh.
It will read that cloud. MD every time.
So the recommendation is really to keep
that within 200 lines. Now, number 18 is
probably my favorite Claude code feature
ever, and that is skills. A skill is a
saved set of instructions for one
specific job written in a file called
skill.mmd. And whenever you hear this MD
thing, that just means markdown file.
And markdown is just a type of computer
language that's very very human
readable. It's super easy to read, but
it just gives computer more structure
when it's reading something. So, you've
got like, you know, section headers and
bullet points and different sorts of
like like bold things like that. So
Claude will basically use a relevant
skill whenever it identifies that it
needs to. Or you can call one yourself
by typing a slash and then the skill's
name. And skills are super super cheap
to keep around because Claude only sees
a short description of each skill until
it actually needs it. Now I myself have
over a 100 skills and the way that most
of them get made is really really
simple. If I've typed the same request
over and over, turn it into a skill. I
typed process this YouTube video into
the Google sheet master database and the
wiki. I've done that probably 15 times
and then I realized, oh, why don't I
just turn this into a skill and now I
have one called process video. And a
skill can be anything. It can literally
be two prompts or it could be an entire
workflow that runs over the course of an
hour. It's just when you turn some sort
of process that already exists into a
reference or an instruction guide that
Claude can then follow for you. So, if
you've ever done something twice, turn
it into a skill. If you ever have
deliverables that you need to create,
turn that into a skill. For example,
once I make a YouTube video, what I do
is I run my process video skill and then
I run my LinkedIn creation skill and
then I run my X article skill and then I
run my upload skill and then I run my
packaging skills. So, I've turned all of
these things into simple SL commands
that I can ask Claude for instead of
having to reexplain myself. So, start
building as many skills as you can. And
that brings us on to number 19, which is
connectors. [music]
connectors plug Claude or connect Claude
into the apps that you already use like
Gmail, Google Calendar, Drive, Slack,
ClickUp, whatever you need. So, it can
actually read and do things in there
with hands rather than just having you
copy and paste everything back and
forth. It's really the big difference
between an agent and just a chatbot.
Now, under the hood, a lot of these run
on something called MCP, which stands
for model context protocol. You don't
really really need to know what that
means. It's sort of similar to an API or
an application programming interface. It
just lets two softwares talk to each
other. So, Claude and Gmail or Claude
and Fireflies connectors also exist on
the free plan, too. And my own command
center pulls in my ClickUp, my Slack,
and my Gmail through these connectors.
Now, number 20 is plugins. A plug-in is
a bundle that you install in one go. And
it can include skills, commands,
connectors, agents, all of these things
packaged together. And by the way, in my
free school community that I mentioned
earlier, I've got tons of free plugins
and skills and docs, tons of free stuff
in there. But Enthropic now has a
directory where people can also submit
other plugins. And companies are
shipping their own like Salesforce which
has a sales plugin in beta. And your own
company can use the same plugins
together. So everyone's kind of creating
the same sort of docs and resources.
Like I have a plugin for my team called
AIS branded doc. Whenever anyone's
making a document that might be
externally facing, they have to run that
skill so that all of our docs feel
consistent and feel on brand to anything
external. Now number 21 is mods. And
it's one of my favorite things in here.
It's kind of recent and it's so so cool.
A mod is a type of plugin that literally
modifies or changes or hacks how Claude
code itself works. You can add new
commands. You can add new tools. You can
even customize the interface or you can
change just little pieces of the
interface like a panel beside your chat
or you can add a little pet in the top
right. And you don't have to code one.
Anthropics docs say that you can
literally just describe the mod you want
and Claude wires it in. So if you've
ever been like, I wish the Claude
desktop app had this, just ask it to do
it and it will build a mod for it. Now
I've got seven of these myself. One of
them saves me money by keeping my
session cached so Claude doesn't have to
reread everything when I come back from
[music] a break. One other one shows a
progress bar whenever Claude's working
towards some sort of goal and it shows
me the drill down of all the tasks. I've
also got a little pixel cat that I
renamed bite and just hangs out on my
screen and tells me when other sessions
are done. So really get creative with
those mods. They're pretty fun, but they
can also be super super super useful
too. Like the one I mentioned earlier
that makes sure that two sessions don't
overwrite the same file. But anyways,
now Claude knows who you are. The last
part is about letting it actually work
on its own. So number 22 is permission
modes, which control how much Claude
asks you before it does something. And
there are five of them. Manual asks
before it edits files or runs commands.
Accept edits lets it change files, but
still asks before most commands. Plan
has it look around and propose a plan
without changing anything. Auto mode
runs without the routine prompts, but a
background check makes sure that each
action lines up with what you actually
asked for. and then bypass permissions
or dangerously skip permissions skips
almost all the prompts. Now, for me, I
always just leave auto on. And this has
been the default for new sessions on
Pro, Max, and Team plans since August.
And if you're nervous, then just start
in plan mode, read the plan, and then
let it go. But auto mode seems to do the
trick for most cases, and it always will
take the cautious side. You'd rather be
safe than sorry. And then number 23, we
have sub agents. Now, a sub agent is a
helper that Claude can send off to do
one specific job. And it works in its
own separate context window if you
remember when we talked about context
windows earlier, and it only reports
back a small summary to the main
session. So, it helps us save those
tokens. So, all the messy research and
searching doesn't clog up your main
conversation. Now, I have this skill
called roast room, which you guys can
get if you want in my community, which
is built on this idea of sub agents.
Basically, I ask it a business question
and each seat on the board like Alex
Ramoszi, Jeff Bezos or Warren Buffett is
its own custom sub agent that I built.
And all of these custom sub agents argue
about my decision before they give me a
verdict and before they give me some
business advice. Now, number 24 is
projects. And this one's a little
confusing because the word means two
different things right now. In the
Claude app, a project is kind of like a
folder for related chats with its own
files and instructions. But in cloud
code, a project is one ongoing
conversation or like a folder that you
have locally where cloud coordinates a
whole system of related work for you.
You tell it what needs doing and it
starts a separate thread for each task
and those threads usually run in the
cloud and in parallel. So they going
after you close your laptop and you can
check on them from your phone. Now the
difference from sub aents is that a sub
agent is a quick helper inside one
session while a project can run a full
session for every task. So cloud code
projects are in beta right now on pro,
max, and ultra and they're still rolling
out. So if you don't see them yet,
that's why. But once again, they get
rolled out to everybody. And that brings
us on to number 25, which is slashgoal.
Normally Claude does one turn and then
we'll kind of stop and wait for you to
think. But with / goal, you give it a
finish line and it keeps working turn
after turn until that condition is
actually met. So just make sure the
finish line is really, really clear. So
there's no question about when it's done
because then you might get stuck in this
loop where it's like, I can't clear the
goal. I can't clear the goal. And it
just keeps saying that. But this has
really become how I use Claude. It's
about 20% of everything that I send. And
a lot of the research behind this video
ran on a single SLG goal. And I've got
one bonus for you guys, which is number
26, which is scheduled tasks. This is
how Claude works even when you're not
there. In the desktop app, you can
literally set up a scheduled task to run
on a schedule, like every Monday or
every morning. And routines are
basically scheduled tasks, but they just
run in the cloud. And these can once
again be triggered on a schedule or by
events from your other tools. I've got
one that updates my stats on the website
every Sunday, and another one that posts
carousels every single 4 hours. And the
cool thing about schedule task is you
can also just create them with natural
language. Hey Claude, build me a
schedule task for this time and when the
schedule task goes off, you run this
skill and then this skill and it
literally will just set it up for you.
So you definitely don't need all 25 of
these on day one. If you only set up
three today, I'd start with the claw MD
one skill for the thing that you do most
and then try out a few/goal prompts. And
then once you've started getting the
hang of this, what I really want you
guys to do next is build your AI
operating system. So, if you want to
check out a full free course where I
show you guys exactly how to build out
an AI operating system with cloud code,
then join the link in the description,
which is my free school community. I've
got the full free course in there for
you guys with a free plugin that helps
you get set up. But that is going to do
it for today. So, I hope that you guys
enjoyed the video or you learned
something new. And if you did, please
give it a like. It definitely helps me
out a ton. And as always, I appreciate
you guys making it to the end of the
video. And I will see you all in the
next one. Thanks everyone.
