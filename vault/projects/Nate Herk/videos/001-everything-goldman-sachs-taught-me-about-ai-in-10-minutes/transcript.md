So, I'm going to give you everything
that I learned after working at Goldman
Sachs, one of the biggest financial
firms on the planet. These are
principles I still follow to this day in
everything that I do with AI. A company
like this doesn't have the luxury of
making mistakes, and one wrong data
entry or hallucination can cost them
millions of dollars, or even worse,
their reputation. So, if one of the
biggest and most trusted financial firms
on the planet follows these principles,
it's because they work. And even if
you're not working at a big firm, these
principles will completely change how
you use AI and the results that you get
out of AI. So today I'm going to share
the five AI principles I learned from
Goldman Sachs which I call vault and
show you how to apply them to your AI
projects. So let's get into it. Okay, so
V is to verify the output. And just a
reminder, this is the framework I
created from the principles I learned
while working there. And these
principles apply whether you're using
claude code, codecs, or whatever new
tool comes out next month. So Verify, I
think a lot of us, myself included, can
get a little too comfortable with AI
because it gives you something that
looks finished and it will deliver it to
you super confidently. It's formatted
perfectly and it probably took about 30
seconds. But something that looks
finished and something that's actually
correct are obviously two very different
things. So Marco Agenti, Goldman's CIO,
has made this distinction between the
reasoning of a model and its final
output. Basically, the way a model
breaks down and analyzes a problem can
still be useful even when the final
answer it gives you is wrong. So you can
use the breakdown to get value from it,
but you still need to verify the result.
And this actually starts before the AI
even generates an answer. So my role at
Goldman was in business intelligence.
And every business intelligence analyst
in my role had to pass something called
data school. We had to understand how
data gets pulled in, how it gets
cleaned, how it gets updated, and how
you turn all of that into something that
people can actually use to make a
decision because every report, every
dashboard, every automation, and now
every AI system is only as good as the
data that's actually powering it. And
your company's data is probably one of
the biggest advantages that it has
because nobody else has that exact
information. They don't have your
customers, your sales history, your
internal processes, your support
tickets, all of that kind of stuff. It's
gold. But if that data is outdated or
duplicated or messy or just wrong, then
plugging it into AI doesn't magically
fix it. It just gives you the wrong
answer faster. So when I use AI tools, I
like to build verification directly into
the processes. You could give the model
a prompt like, "Hey, you know, before
you give me the final answer, recheck
every number and factual claim. Cite the
source for each one and flag anything
that you're not fully 100% confident
about." And you don't have to manually
verify every single word that it gives
you. If you're creating a report, maybe
there are only two or three numbers that
could actually change the decision. So
have the model site those numbers and
then you can spot check them yourself.
And obviously for higher stakes projects
you can even build a separate AI
reviewer or multiple you know like a
team of AI agents that are just there to
review. They'll check the first output
before you see anything and then the
whole system can iterate once again
before you see anything. And that's an
additional check. But important claims
still need original sources,
deterministic tests or human review. So
verify the data going in, verify the
important outputs coming out and build
review into [music] the process. But
once you can trust the inputs and the
outputs, you still have to decide
whether AI should be in the workflow at
all. So moving on to a augment, which
means augment don't replace. Now my
full-time job at Goldman was basically
building automations, reports,
dashboards, and systems that made teams
more efficient. [music] And across the
teams I worked with, there were people
doing some version of that work. None of
this was some brand new AI initiative.
You know, Goldman had been building
automated data and risk systems for
decades. and teams across the firm were
doing this kind of work before the
current wave of AI agents hit the
market. Which means there were already a
crazy amount of problems worth solving
before anyone started talking about AI
agents. There were manual reports being
built that took hours. You know, data
had to be moved between systems. Teams
were waiting on information from other
people. People would enter something
incorrectly with a fat finger or skip a
step or or two people would follow the
same process in two slightly different
ways. [music] Because at the end of the
day, humans are inconsistent. We get
tired. We miss steps. communication
breaks down and everybody makes
mistakes. But a properly tested
deterministic automation will run the
same process the exact same way every
single time. Now, that doesn't mean an
automation is automatically correct
because obviously if you build the logic
wrong, it's going to repeat that same
mistake perfectly every single time. But
because it's deterministic, meaning
predictable, it's much easier to test,
to audit, and to fix. So, if a task
follows a clear set of rules, you
probably don't need an AI agent. Use AI
when you need judgment, interpretation,
flexibility, or the ability to work
through messy information. But use
normal automation when the steps and
correct answer are already known. And
this is really important because in this
hype wave of AI, everyone thinks, "Oh,
we have this problem. Let's use AI to
solve it." But if you can come in here
and say, "You know what? Actually, if we
didn't use AI, this would actually be
cheaper, faster, and probably better."
That perspective is really valuable as
well. And honestly, a lot of the best
systems will combine both. Let's say
you're creating a weekly business
report. A normal automation can pull the
numbers from your database, clean them
up, run the calculations, and verify
that nothing is wrong. And then you can
have an AI model look at those verified
numbers and explain what changed [music]
in plain English. The deterministic
system handles the facts and AI helps
you tell a story from it. That's what
augmenting an existing process looks
like. You take something that already
works, break it into steps, and then you
improve the specific steps where AI can
actually help. Once again, don't use AI
to solve a problem that a simple
automation can already solve. And
choosing the right approach gets a lot
easier when you understand why you're
building the system in the first place.
Which brings us on to the U of Vault,
which is to understand the why. One of
Goldman's engineering principles is
called build with purpose. Marco Agenti
explains it by saying that engineers
can't focus only on the how. They need
to prioritize the why. And I see people
do the exact opposite with AI all the
time. They open up an AI tool thinking,
I want to build an agent, or I want to
make a workflow, or I want to use this
new tool that everyone's talking about,
but what's the problem you're actually
solving? You can build a really
impressive workflow that nobody needs.
You can spend an entire week getting an
agent to work perfectly, and if it
doesn't save time, make money, reduce
mistakes, or improve some actual
outcome, then what's the point? So start
with the problem and then choose the
tool. Before you open an AI tool, just
write one sentence. The problem I'm
trying to solve is blank. And a good
result would look like blank. And if you
can't write that sentence, then you're
probably not ready to start prompting an
AI model yet. Because if you don't know
what you want, then how is the model
supposed to know that either? And if
you're still figuring it out, that's
fine. You can use AI as a brainstorming
thought partner. You know, give it the
context, explain the bottleneck, and ask
it to help you find the simplest way to
solve it. This is especially important
if you're trying to make money with AI.
Inside my communities, I've seen people
build every workflow imaginable and
still struggle to get clients because
they started with the tech. I've also
watched completely new members focus on
one painful problem, build one useful
system, and replace their job income
within months. The difference was the
problem that they chose to solve. And
speaking of the community, if you guys
want to learn how to use AI tools and
get free resources that help you move
faster, then you can join my community
for completely free. I've put courses in
there and I've also put everything that
I'm talking about in today's video with
the vault framework, a full resource
guide around that in my community.
There's also stuff in there about how to
start a business using AI. So, if you
want to join, the link for that is down
in the description. We're almost at half
a million members in there, which is
just awesome. So, I'd love to see you
guys in there. Let's get back to the
video. Okay, so now we're moving on to
the L, which is loop humans in. Think
about AI kind of like a megaphone.
Whatever you give it can be amplified
across an entire workflow, including
mistakes. A slightly unclear instruction
might give you one slightly wrong answer
inside a chat, but once you connect that
same instruction to an autonomous agent,
it could send the wrong email. It could
update the wrong record. It could
publish something publicly or message an
entire client list before you even see
it. We actually had an autonomous AI
agent that looked at a task list,
proactively took one off the list,
interpreted that wrong, and ended up
sending a discount code to almost
200,000 people on our email list.
Obviously, big mistake. Marco Agenti has
warned about this exact problem. A small
miscommunication can get amplified by an
AI system. And when agents take action,
hallucinations can lead to incorrect or
even dangerous actions. I'm sure we've
all heard those horror stories of agents
deleting massive databases at massive
companies. But anyways, Argenti's
conclusion is pretty simple. Until these
tools are consistently reliable, humans
have to stay in the loop. That doesn't
mean a person needs to approve every
single tiny little action, your level of
oversight should basically match the
consequence of the action. If an AI tool
is organizing your personal notes, let
it run. If it's preparing something for
a client, you know, changing important
data or spending money or communicating
with a large group of people, then add
an approval step, please. One of the
easiest ways to do this is to set your
automations to draft, not to send. Have
the AI write emails into your Gmail
drafts. Have it put proposed replies
into a document. Whether you're using
cloud code, codecs, or whatever else,
have it show you the plan before it
changes any important files, deploys
anything, or takes an action that you
can't easily undo. You still obviously
are getting most the speed, but one
weird output doesn't immediately turn
into a much bigger problem. The more
people an action can affect, the more
important the human checkpoints become.
A guiding rule that we talk about inside
my team is if the agent could
potentially do something, then you have
to assume that it will because 999 times
it might do what you want, but that one
time it could be bad. And the thing is
that human can't properly approve the
work if the system doesn't show them how
it reached the result. Which brings us
on to the T which is for transparency.
At a company like Goldman, if you build
something that touches important data,
reporting or risk, then you need to be
able to explain where the information
came from, what happened to it and how
the final result was actually produced.
[music] They have regulators, clients,
managers, and other teams that may need
to review those decisions. You can't
defend something that you don't
understand. And you should build your
own AI systems the same way. If an agent
works, but nobody understands how it
works, then it's going to be a nightmare
when something breaks, when the data
changes, or when somebody else needs to
take over that project, because you
might not know what to fix or which step
failed, and you probably won't be able
to repeat the results consistently. So,
ask the AI to document what it's doing
as it builds. Every single execution of
these systems needs to be logged
somewhere, listing its data sources,
assumptions, tools, validation checks,
and any important decisions. If it
produces a report, ask it to show which
source supports each conclusion. If it
creates an automation, have it explain
what triggers the workflow, what happens
at each step, and where a human needs to
approve something. And transparency
doesn't mean asking a model to reveal
some hidden internal thought process.
What you need is evidence that you can
actually inspect the sources, the
inputs, the actions, the assumptions,
and the checks that it ran. That makes
the system easier to trust, easier to
improve, and so much easier to hand off
to another person. Okay, so those are
the five principles inside Vault. Verify
the output, augment the systems that
already work, understand the why, loop
humans in, and keep the entire process
transparent. And I think the biggest
lesson that I took from Goldman is that
you don't need to make everything an AI
agent. You need to understand the
problem, protect the data, use the
simplest system that works, and keep
control over the actions that actually
matter. That's how you build AI systems
that you can trust. And if you want to
turn these principles into actual
projects, my free community has courses
and resources that can help you get
started. There's a full path to building
an AI portfolio in 7 days, learning AI
tools, and creating your first agents
and systems. And if you want more direct
help and a path to getting your first
client and spinning up your own
oneperson AI agency, then you can check
out my road map in the link in the
description. But anyways, that is going
to do it for this one. So, if you guys
enjoyed the video or you learned
something new, please give it a like. It
definitely helps me out a ton. And as
always, I appreciate you guys making it
to the end of the video. I'll see you in
the next one.
