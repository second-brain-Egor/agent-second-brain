Today I've got four tricks from
Enthropic themselves on how to get more
out of Fable 5.1, how to use it more
efficiently, and how to stretch that
weekly usage limit as long as it can go.
So, let's not waste any time and just
get straight into today's video. Okay,
so before we hop into these things, I
wanted to say that I really am liking
Fable 5.1 so far. I will be honest, as
of lately, I've been using Codeex a lot
more than Claude Code, but Fable 5.1,
it's feeling really nice. It's feeling
pretty quick and it's feeling pretty
efficient if you learn to use it right
because I have seen tons of people
complaining that they are just killing
their session limits. So, let's get into
it today. Now, everything that I'm
talking about today, I found straight
from the Claude platform docs on how to
prompt Claude Fable 5.1. There's a ton
of gold in here and it talks about every
individual model because these are
different models. They have different
characteristics and they perceive
information a little bit differently.
So, it's always worth checking out.
There's a ton of info in here. Like,
this is a long long doc with lots of
scenarios. So, I dug through here and I
just pulled out what I think you guys
actually need to know to start using it
differently right now today. So anyways,
the first one, tell it what done looks
like. This means you're not giving it
tasks, you're giving it the finish line,
and you're letting Fable 5.1 figure out
the tasks that need to come together to
create the end result. I've heard Boris
Churnney, the creator of Claude Code,
say so many times to give these models
an ambitious goal, and get out of their
way. So tell Fable the outcome, tell it
why it matters, tell it what done means,
and tell it if there are any real
constraints. So instead of saying
something like
out.
&gt;&gt; So instead of saying something this
wordy, could you just shorten this down
into one overall goal without defining
all the individual tasks?
Boom. Now we have create an appealing
landing page offering voice agent
solutions tailored to our target
audience. And then it will find out what
it needs to do. Now, for all of these
tips, what I'm going to do is show you
guys real quotes and real evidence from
this documentation where I pulled these
tricks from. But what I did want to show
you real quick is that some of these
will be coming from the Claude Fable 5
docs. But I wanted to show you guys this
right here. Your existing CloudFable 5
prompts should perform well on Claude
Fable 5.1 without changes, but a handful
of behavioral differences are worth
knowing about. So this document
prompting Claude Fable 5.1. A lot of
this is just like in addition to the way
that you prompt Cloud Fable that you can
find in this doc. So I just needed to
make that quick disclaimer as you can
see. But anyways, let's get into some of
this evidence here. So this first piece,
Claude Fable 5 tends to perform better
when it understands the intent behind a
request. Context lets it connect the
task to relevant information rather than
inferring intent on its own. So provide
context about why you're asking,
especially for longunning agents drawing
on multiple work streams, which is why
building out your own AIOS that has
information about context, your your
goals, your background, that is so
helpful in driving powerful models like
this. This next one here, refactor
existing prompts and skills. skills
developed for prior models are often too
prescriptive for Claude Fable 5 and
Fable 5.1. Meaning, if you have some
skills that are literally like, do this,
this, this, this, this, like so, so
specifically, that is kind of the way we
were taught to build skills, but that
might actually be getting in Fable 5.1's
way where it's making it less efficient
and it's kind of just like putting guard
rails on it. And the whole idea of like
rerunning your skills for different
models is really real. It's something
I've said before and I wanted to show
you guys this this tweet that I saw
today from Peter Yang. If you're trying
out Fable 5.1, I highly recommend
running/claw- API prompt- audit. Run it
on your skills. It finds a bunch of
redundancies and rules to remove for the
latest models. So, go ahead and try
that. And then this last piece here was
about finishing the whole task. Cloud
Fable 5.1 can execute very long tasks
without much guidance on methodology,
especially when the goal is clear. But
that's the key there. The goal has to be
very clear. So, that is why tip number
one was to tell it what done looks like.
Do it in a way where you're not giving
it task after task after task. All
right. Number two, we have to match the
effort to the task. How many of us just
hop on a claude and we don't actually
drag the effort slider around and we
just stay at high? Because as you guys
know down here, when you click on the
model, you obviously choose that there.
And when you click on the effort level,
you can change this from high to medium
to low to extra to max or to ultra code.
And by default, Claude Fable 5.1 just
sits on high. But take a look at these
benchmarks, which is really interesting.
Over here, you can see Fable 5.1. Let's
just look at the version with no tools.
And you can see Fable 5 with no tools.
And the point I'm trying to make right
now isn't that 5.1 is much more
efficient or better than five. The point
I'm trying to make here is that it
really differs. Fable 5.1 on low is so
much different than Fable 5.1 on max.
Fable 5.1 on low is about comparable to
Fable 5 on medium or high, but it's also
cheaper. I've also heard people compare
Fable 5.1 on low to things like Opus or
sometimes a really, really good sonnet.
Now, the point I'm trying to make here
is the majority of work that you're
probably doing with Fable 5.1, Fable 5.1
on high is overkill. I see this meme on
Twitter where it's like this guy is
lighting a cigarette with a blowtorrch
and it's like using Fable 5.1 to
reorganize my downloads folder. Like the
normal model nowadays, Sonnet, you know,
GBT 5.5, like these older models are
still really, really good. Like remember
when Sonnet 3.7 was like the best thing
out there? It's still a really good
model. It's just that we have things
that are so much better now that that
doesn't always have to be the default.
So, the point I'm trying to make here is
do not automatically run everything at
maximum effort or even just high. Start
with high, then test whether medium can
do that same task just as well. And if
it can, try it on low. And you only need
X high and max when you're doing like
massive massive work or something that
needs like deep deep thought. And
obviously, that kind of stuff is going
to cost you a little bit more as well.
Okay, so let's take a look at some
evidence here. The first one is to
consider all effort levels. Pretty much
just what I said. Start with the default
at high, then test on other levels like
low, medium, X high, and max against
your own EV valves is what I think is
really clear because some people are
like, "Oh yeah, I drive all the time
with X high and it's it's perfect for
me. Anything lower and it's not as
good." Well, maybe they're doing like
deep software engineering and, you know,
merging 15 PRs every second. That's
probably something that does need X
high. But maybe you're creating
documents and creating spreadsheets that
probably doesn't need X high or high.
So, it has to be on your own evals and
your own use cases. The next one we have
here is search triggering at low effort.
So just think about this. At low effort,
CloudFable 5.1 is less likely than
CloudFable 5 to call a search or
retrieval tool and more likely to answer
from memory. So there are lots of decent
use cases for switching CloudFable 5.1
to low when you still want that Fable
5.1 feel, but maybe you don't need to be
doing all of this tool calling as much
and you're maybe ideulating,
brainstorming, searching for things. And
then look at this about changing effort
mid-con conversation. You can run later
turns of a conversation at a different
effort level in two ways. Now on Claude
Fable 5.1, you can use a per message
effort change which keeps the prompt
cache. But on other models, you have to
set a new top level on the new request.
So Fable 5.1 lets you switch effort in
between questions, in between texts,
which is pretty cool, in between turns.
All right, moving on to number three
here, which is my favorite one of all
time, not just for Fable 5.1, but just
in general working with AI, is to make
it prove its work. So think about how
would you check this output if a human
came to you and gave it to you? What
would you do? Would you just look at it
like a website? Would you watch the
video? Would you try to like look up the
sources and fact check? Would you test
the UI by clicking? Whatever you would
do here, apply your own taste, apply
your own judgment. Let the AI models do
it first. The whole idea is you don't
want to get handed a rough draft. You
want to get handed a version five or a
version 10 that's already been approved
and reviewed by lots of little sub
agents that do verification and then
it's been iterated on like five or six
times or maybe even 10 times because
every single time they review it, they
find a mistake, they fix it, they review
it again, they find a mistake, they fix
it. Now the tough part is not every
single piece of output can have an
objective check. Like if you were
literally trying to optimize the
performance of something so that X
equals 10, that's something that
objectively can be proven. A lot of
these sorts of outputs need to be
verified from more of a subjective
level, which is really you creating your
own sort of like LLM as a judge, which
means that you do have to put your, you
know, input in there as far as this is
what good looks like. So, you define the
goal, but you also need to very firmly
define what does good look like and how
do you test if X is good. So, it's not
going to get you 100% of the way there,
but you'd rather get 97% of the way
there than getting like 70% of the way
there. You know what I mean? And here's
some evidence from the docs. You can see
this first one is make self-verification
explicit in long run prompts. So
literally telling it here verify your
work with sub agents against the
specification. Down here another one you
can see in the prompt it says verify
your work however you like. And then
down here we have um before reporting
progress audit each claim against a tool
result from the session. Only report
work you can point to evidence for. If
something is not yet verified, say so
explicitly. And then just on the vision
piece, because I know a lot of us are
building websites or slide decks or
whatever it might be where you need some
vision verification, Claude Fable 5.1
has better vision capabilities out of
the box and on complex visual inputs
such as dense charts. It does its best
work when it can iteratively analyze,
crop, and visually verify what it sees
as it goes. And finally, moving on here
to number four, we have parallelize and
delegate. So breaking a large task into
independent tasks. Just because you have
one process doesn't mean one agent needs
to be working on it. You can have one
process where you actually have 80
agents each go in there, pick one piece
of it, like an assembly line, and they
hand stuff off to each other, or they
all do their own piece at the same time,
and then it all comes together in the
end. Not every task is available to be
like parallel work, but a lot of them
are. So, this will give you faster
completion, better focus and specificity
because each agent has one very specific
job now and they'll just they're going
to do better broader coverage and
context efficiency because now you can
keep that main session cleaner and
conversate with you while you have it
delegate out to a bunch of different
agents. And this is like the most
important thing that I've been able to
do to get way more usage out of my Fable
5.1. Most of the time now when I'm
working with Fable 5.1, I tell it, I
don't want you to build anything. I
don't want you to code anything. I don't
want you to research anything. I just
want you to spin up sub aents, drive
strategy, interpret what they give you,
and then spin up more sub agents because
now we're getting Fable's intelligence
to do that, and we're saving so many
tokens. Trust me, just try out using
some prompts like that, and you will
feel the difference immediately. But
that doesn't mean that Fable isn't
responsible for the outcome. Like, if
it's a bad output, then it was Fable
5.1's fault, not all the sub agents
faults. So, it needs to keep in mind
that it still has to do things like
spinning up verifier agents or maybe at
the very very end on the final pass
before it gives it to you the human.
Maybe that's when Fable 5.1 actually
steps in there and it gets its hands
dirty a little bit at the very end.
Anyways, let's look at some evidence
here. So, the first one, delegation and
collaboration. Cloud Fable 5 is
significantly more dependable at
dispatching and sustaining parallel
agents and reliably manages ongoing
communication with longrunning sub
agents and peer agents. Then we have
batching independent tool calls. Fable
5.1 usually issues parallel tool calls
as expected. When a request names
several things to fetch, it issues those
calls all in parallel so they can all
work at the same time and you're not
just sitting there wasting time. And
once again, parallel sub agents save
time and cost through cache reads and
avoid bottlenecking on the slowest sub
aent. If you got an assembly line and
agent number three is just taking
forever, then 4 5 6 7 8 9 10, all of
those other agents are just sitting
there and waiting. So if you can
parallelize them, parallelize them. So,
I know that was a decent amount of
information that we just covered and I
put all of this information with all of
this evidence into just a super simple
resource guide that you can access for
completely free. All you have to do is
go to my free school community. The link
is down in the description. You'll come
into here, you'll click on classroom,
you'll go to all YouTube resources and
every free doc or skill or repo or
guide, whatever it is, I've always given
them away for free right inside of here.
So, that is going to do it for today's
video. I hope you guys enjoyed or
learned something new. And if you did,
please give it a like. It helps me out a
ton. And as always, I appreciate you
guys making it to the end of the video.
I'll see you on the next one.
