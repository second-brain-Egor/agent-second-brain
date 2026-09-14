So, Enthropic Engineers just said that
they stopped building agents and they
started building something completely
different. So, if you're still focused
on building agents, you're probably
wasting hours on something that'll never
work the way that you actually want it
to. But if you focus on what these
engineers are actually building, you'll
have a system that improves on its own.
So, in this video, I'm going to show you
what they said to build instead and the
four things that actually make it work
so that you can start getting the same
quality results that Enthropic engineers
are getting. So, let's get into it. All
right. So, Enthropic isn't saying that
agents are dead. Barry Jien and Mahesh
Marog, the two people who created agent
skills adanthropic, said that they
basically stopped rebuilding a separate
agent for every single job because the
agent underneath had become way more
general purpose than they expected. So,
real quick, the easiest way to
understand this is to look at your
phone. Your phone has a processor, an
operating system, and then all the apps
that you actually use every day. And a
few massive companies build the
processor and the operating system. You
probably aren't changing either one of
those things, but you can choose the
apps, and each app gives that same phone
a very specific capability. And the
whole AI stack is starting to look
pretty similar to that. The model is
kind of like the processor. The agent
runtime is like the operating [music]
system. And then skills are the apps. So
cloud code can already read files, write
code, call tools, and work through a
task. You don't need to necessarily
rebuild all of that every time that you
want help creating a presentation or
researching a company or writing a
LinkedIn post or doing whatever kind of
things you need to do like that. You
give the same general purpose agent a
skill that contains the process, the
context, the scripts, and the examples
for that specific job. So now let me
talk about the four practical ways to
make those skills work better. So the
first one is simple. Stop making Claude
solve the same technical problem over
and over. And team kept watching Claude
write basically the exact same Python
script every time it needed to apply
styling to a slide deck. It would spend
tons of tokens just recreating the code
that has already been written. And
because it was rebuilding it from
scratch, the result could change from
one run to the next. So it wasn't super
consistent. So what they did is they had
Claude save that script inside the skill
as in their own words a tool for its
future self. So now the next time it
needs to style a presentation, it can
just run the version that already was
proven to work. And developers have
followed this idea forever. It's called
dry or dr, which stands for don't repeat
yourself. If you solve a problem in
code, you can just save the solution and
reuse it instead of rewriting the code
every single time. And you can do the
exact same thing with Claude. I've got
skills in my own AI operating system
that use the same renderers, the same
templates, scripts, and stuff like that
every time. My carousel workflow doesn't
ask Claude to reinvent how a slide gets
rendered on every run. the skill just
points it to the files that already work
and then Claude can just focus on the
new content. Like literally just
changing the text. So the next time
Claude writes a script that gives you a
result that you really like, don't leave
that code trapped inside the chat just
to get lost later when you start up new
sessions. Tell it something like save
the script you just used inside the
skills script folder. Update the
skill.mmd so that future runs execute
that file instead of trying to rewrite
it again. Then I want you to run the
skill again and verify the result. And
real quick, you still obviously need to
test it. You run the same type of task
twice. You compare the important parts
and make sure the skill is actually
calling the saved file. The surrounding
AI output may still vary a little bit,
but you've replaced one fresh guess with
a proven piece of code. So, moral of the
story, don't pay Claude to rediscover a
solution that you already have. But once
you start building a bunch of these
skills, Claude needs to know which one
belongs to the job in front of it. So,
let's move on to number two. So, think
about a mechanic for a second. A
mechanic might own hundreds of tools,
but he doesn't dump every single one
onto the bench before he starts changing
a tire. He basically just identifies the
job and grabs the few tools that he
needs and leaves everything else inside
the toolbox. And skills work in a very
similar way because of something that
Enthropic calls progressive disclosure.
So when Claude starts, it doesn't read
the full instructions and all the
examples and all the scripts from every
single skill you have. That would be a
huge waste of time and tokens. It starts
with the name and the description of
each skill. And this is called the YAML
front matter. Then when your specific
prompt matches a description of a skill,
that's when it reads the full skill. MD
file. and any larger references or
scripts can just stay in the folder
until the task actually needs them.
Enthropic describes this as letting
Claude load information only as needed.
That basically keeps irrelevant
instructions out of the working context,
which helps you avoid the bloat and
confusion which sometimes gets called
context rod. But this depends on your
description being really really clear.
If one skill says help with content and
another one says create marketing
assets, then cla basically guessing
because those descriptions sort of
overlap and they don't tell the agent
when either of those skills should
actually run. So, a stronger description
might say something like, "This skill
creates LinkedIn carousels from a topic,
from a transcript, or an outline. Use
this when the user asks for a carousel,
carousel slides, or a LinkedIn document
post." Now, Claude knows what the skill
does and exactly when to use it. So,
just keep each skill focused on one
specific job. Put the words a real
person would use inside the description
and make sure two skills aren't
competing for the same request. And you
can actually have Claude Code audit this
for you. [music] Just say, "Hey, review
all my skill descriptions. For each one,
tell me what it does, when it should
trigger, and where it overlaps with any
other skills. Rewrite only descriptions
that are [music] ambiguous. And then you
can test these three things. The first
one is an obvious request that should
trigger it. The second one is a
differently worded request that still
should trigger it. And the third one is
an unrelated request that definitely
should not trigger it. And just remember
that a skill that Claude can't find is
basically a skill that you don't have.
So finding the correct skill handles
today's tasks. But the next step is
actually making sure that the skill gets
better every single time you use it. So,
number three, every time you correct
Claude and then you close the chat,
there's a pretty good chance you just
threw that lesson away. Maybe [music] it
used the wrong tone or it skipped a
validation step or maybe it formatted
the final output in a way that you don't
want to see again. And if all you say to
Claude is fix it, then it probably will
fix it, but the process stays broken.
And this is something I've had to work
through inside my own AI operating
system. If an agent tells me it can't
find a file that I know exists, I don't
just hand it the path and keep moving. I
ask it to backtrack. I basically ask it
to show me its work, show me where it
searched, figure out why it missed the
file, and then update the routing or the
skill so that next run starts in the
correct place. Enthropic designs skills
as a step toward this kind of continuous
learning. Their guarantee is that
anything that Claude writes down can be
used efficiently by a future version of
itself. Now, here's the thing. Skills
don't remember every single thing, and
they aren't a recording of every
conversation that you've ever had. They
basically store the procedural knowledge
that Claude needs to do the [music]
specific job. So, when a process is
wrong, update the instructions in the
skill.mmd. When Claude is missing your
voice or your brand or your examples,
then add a reference file. And when the
same mistake keeps happening, then add a
clear rule that explicitly prevents
that. And then rerun the same task. You
could use a prompt like this. Review
what went wrong during this run. Decide
whether the cause was the process or
missing context or a weak rule or
unreliable code. And then update the
skill in the smallest durable place.
Then rerun the same task and verify
[music] the fix. Over time, the skill
becomes a living record of how you want
the job done. And I do want to be
precise about the phrase model proof. No
skill can just force a weaker model to
perform exactly like the stronger one.
Different models will obviously still
produce different results and they
interpret skills in different ways. But
your process can be portable. Agent
skills are an open format. So the same
core like skills folder can work across
compatible agent harnesses like codeex
or Hermes agent or anything else. So
test an important skill with another
compatible agent. If the result falls
apart, then look for hidden assumptions,
missing examples or instructions that
only one model understands and then
tighten up the skill and keep testing.
All right, so the first three were very
important, but this one is probably the
most important. A skill shouldn't hand
you its first attempt and call the job
done. This is probably the biggest gap
that I see with a lot of AI workflows.
You run the skill, it creates the thing,
saves the file, and then comes back to
you and says, "Hey, I'm done." And then
you open it and you realize that the
formatting is broken, the sources don't
support the claims, or that the script
falls completely flat for the person
you're trying to reach. So, the AI did
maybe 70 or 80% of the job, and now
you're the human, you know, manually
doing the last 20 or 30%. But if you
already know how to personally check
that work, then just bake those checks
into the skill and let the AI close more
of that gap for you. So, for example,
for a slide deck, have the skill render
each slide as an image, inspect the
screenshots, fix anything that's cropped
or hard to read or out of bounds, and
rerender it. For a research report, make
it open the primary sources, match the
claims [music] to the evidence, and
remove anything that it couldn't
actually verify. And if you're creating
a script or an ad or something more
subjective, then have a few different
personas, like a few different sub
aents, review it and discuss it. A
beginner agent can tell you where
they're confused. [music] A skeptical
buyer agent can tell you what they don't
believe. Someone from your actual
audience can tell you where they would
probably click away. Now, you don't have
to accept every single piece of feedback
that you get from these different agent
personas. That would probably make the
output worse, but the skill can find the
issues that show up more than once, make
the strongest revisions, and then run
the review again. And sometimes just
hearing those different perspectives is
really helpful. And real quick,
verification isn't clawed reading its
own work and saying, "Looks good to me."
It needs some kind of evidence outside
of that first draft, whether that's a
screenshot, a test result, [music] a
source, a reference example, or like I
said, feedback from a few different
agent perspectives. And you can add
something like this into almost any
skill. Say something like, "Before
returning the final output, define the
acceptance criteria. Create the first
version, inspect it using the relevant
verification method, fix every issue you
find, and then run another pass. Return
the output only after it meets the
criteria with a short summary of what
you checked. And if something can't be
verified, then tell me exactly what
remains. It's even better if there's
some sort of objective success metric
that you can set and just have the
agents keep working until it hits that
objectively. But anyways, now the first
output is basically an internal draft.
Claude reviews it, catches the obvious
problems, and then improves it before
you see any of it, before you waste any
of your time and attention on it.
Because you're ultimately still going to
be the final judge, especially when
there's things like taste or strategy or
business judgment involved in the
process. The goal, though, is just to
stop spending your time catching
problems that the AI could have caught
on its own. Your first look should not
be the agent's first look. It should be
the agent's, you know, fourth or fifth
or maybe even sixth look. So now you
know what enthropic engineers are
actually building. They save proven code
instead of rewriting it. They give every
skill a precise description so Claude
loads only the correct one. They turn
corrections into durable instructions
that keep improving. And they verify the
work before it ever reaches you. That's
how you take a general purpose agent and
you teach it how you work specifically.
And if you want to see how I organize
the agents, the context, connections,
capabilities, and cadence around all of
this, then I'll put my full AI operating
system course on screen right up here. I
also have free courses, templates, and
resources inside my free community that
will help you build agents and workflows
from scratch. You can join with the link
in the description. And if you want to
go deeper [music] on turning these
skills into a career, then you can check
out my plus community. But anyways, that
is going to do it for this one. So, if
you guys enjoyed, you learned something
new, please give it a like. It helps me
out a ton. And as always, I appreciate
you guys making it to the end of the
video. I'll see you on the next one.
Thanks everyone.
