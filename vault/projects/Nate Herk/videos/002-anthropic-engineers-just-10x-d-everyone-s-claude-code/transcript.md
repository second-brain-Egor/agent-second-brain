---
type: project
last_accessed: 2026-10-09
relevance: 0.98
tier: active
---
So, Enthropic engineers just 10xed
Claude code by deleting over 80% of its
system prompt. But they also changed
everything that we know about prompting.
Because a lot of us were told the best
way to get Claude to behave the way we
want it to was to give it as much
information in context as possible. But
with this change, almost all of your
information is actually slowing Claude
down and slowing down its thinking
speed. So today, I'm going to show you
how to fix your projects using the
engineering approach from Enthropic. So
let's get into it. All right. So Thoric,
one of the engineers at Enthropic,
recently published an article called the
new rules of condex engineering for
cloud 5 generation models. His team
removed over 80% of cloud code system
prompt for models like Opus 5 and Fable
5 and 5.1 and future models and they
reported no measurable loss on their
evaluations of these models. The system
prompt is basically the rulebook that
comes with cloud code. So your own
instructions and whatever context gets
loaded for the task sit right alongside
of the system prompt. So they're saying
that they could cut most of that
rulebook and keep the performance that
they had measured. And in my own setup,
I used their guidance to review the
instructions that I had accumulated and
clean up how my skills work together.
And this goes right alongside with Boris
Jurnney, the creator of Cloud Code set
himself, which was basically like every
6 months, you should delete all of your
skills. And we've been told that skills
are what makes Cloud Code much smarter
and much more consistent. Now, describes
that rules they needed for older models
became too restrictive as Claude
actually just got better and better. One
example was comments in code because
they used to put a hard limit on how
much Claude could write, even though
some projects needed more explanation.
[music] The replacement now tells it to
follow the style of the surrounding
code. I think it's pretty easy to end up
with the same problem in your own setup.
You know, Claude makes a mistake, you
add a rule, and then a few months later,
you've got that rule in your cloud.MD
file or in a skill, maybe a slightly
different version of it somewhere else,
and you don't actually need that rule
because you keep upgrading the model,
but the instructions still stay in
there, and the model might not need all
of that extra context. Now, I recently
did a video about prompting fable 5.1. I
talked about the idea of defining to the
model what done looks like. You
basically need to give it the outcome
that you're after, why you're doing it,
and the constraints that it needs to
respect. And then you just have to get
out of its way. Leave it some room to
actually do [music] the work. So for
this video, I asked Claude to look at
how I get from a YouTube idea to a
script that I could film [music] or an
outline that I could film about. And I
wanted it to find a small improvement
and point me to the file so that I could
check the recommendation for myself. So
I'll show you guys that demo of me
actually doing this later in the video.
Now, Enthropic's applied AI team
recommends using the smallest amount of
context that gets the result you want.
And I turned that into sort of my own
saying, which is the best context is the
smallest amount of context that gets you
the highest quality result at the
cheapest cost. They also explicitly say
that minimal doesn't necessarily mean
short. If the model needs a detail to do
the job, then obviously you need to keep
that detail in there. And there's
research looking at what happens when
you add more input. A paper published in
2025 tested five models on math,
question answering, and coding. And
performance dropped as the input got
longer, even when the models could
retrieve the relevant information. The
reported drops ranged from 13.9% to 85%
depending on the model and the task. Now
those were obviously different models
and that was you know over a year and a
half ago and these were controlled
experiments. So those percentages don't
tell us what will happen when you trim
your own cloudmd for example. But
Enthropic also tested loading MCP tool
definitions only when needed. They
reported an 85% reduction in token usage
in their example and their MCP
evaluation scores improved from 49% to
74% for Opus 4 and from 79.5 to 88.1%
for Opus 4.5. So there are measured
results behind this exact idea. And in
that case, Claude still had access to
the tools. It just didn't have to load
all of those instructions up front. Now
in your own setup, you can use a
/docctor. And when I recently did this,
the doctor report gave me this workflow
audit with specific instructions and
handoffs that I need to clean up. So,
I'm also going to show you guys that in
just a sec. Real quick, guys, a message
from today's sponsor, Hyper Agent. If
you're building agents for clients, most
of the work lands around the agent
because each client's data has to stay
separate. Their staff needs to use it
without breaking it. And somebody has to
be obviously paying for those runs. So,
what Hyper Agent does is they give every
client their own workspace. So, the
agents, the skills, the memories, and
the documents all live inside one
perimeter. So, nothing from one client
shows up in the, you know, the context
of another agent. and your builders work
in there with full edit access and the
client's own staff can get a role that
runs the agents but can't touch the
system prompts or swap the models or
accidentally delete a skill or anything
like that. So, if that sounds useful for
your agency, then check out Hyper Agent
through the link in the description.
Huge thanks to Hyper Agent for
sponsoring this part of the video. Now,
let's get back to it. Now, I have tried
some pretty extreme versions of this
just experimenting with my own AI
operating system. You know, I've
duplicated it before. I removed the
cloudmd. I've removed my skills and I've
tried off, you know, a bunch of
different prompts to see them do the
same job. So, one example that I
recently did was I took this interview
with Boris Journey and I wanted to turn
it into a student resource guide. Now,
my full AIOS setup that I was used to
running every day, it made the prettier
document because it had my branding. It
had a proper heading. It had links that
I normally include. And it had just like
more specific context about me, all that
kind of stuff. And the fresh version
looked a little bit messier. It wasn't
as pretty, but its structure was much
better. It had better details. It
organized the interview into ideas and
it added timestamps. And it just felt
more professional. And it felt like a
better guide to actually give to a
student. So what I had was a polished
guide from one version and a content
structure that I preferred from the
other version. Now obviously I still
want my branding. So what I would do is
I would build a new skill out of this
and I would say, "Hey, you know, you
should be using this as the header and
this as the font and this as the footer
and add these logos and things like
that." But I'm going to leave it up to
you to actually structure the content in
the way that you see fit because I've
gave you the basically the intent of
turn this into a student resource guide.
Because in the pretty version that had
my skill already, I had so many guard
rails and so many instructions that I
was basically just like confining the
model and I wasn't letting it truly be
creative and give me the output that it
thought was best because it was reading
my skill and it had to follow my
instructions. And those instructions
were helpful back when we had like Opus
4, but now that we have Fable 5.1, it's
able to just do a better job on its own.
It's kind of like giving an experienced
designer the checklist that you would
give to a kid making their first
presentation because the designer still
needs to know who it's for and what
you're trying to accomplish. But if you
dictate the placement of every box and
every sentence before they've even seen
the material, you might prevent them
from coming up with something that they
might add that you would actually like
more. And that's how I think about
reviewing these instructions. I want to
keep the details that help Claude
understand the job and what makes it
specific to me and then test it whether
it still needs the procedure that I've
written around it. So when I talk about
the context part of my four C's of an AI
OS, this is the kind of information I
mean. I mean my voice, I mean my goals,
I mean my audience and the way that my
business works. Claude can't just infer
all of that or look it up online. So
that's what I have to supplement to it.
Now, it's also important to explain why
you're asking for something, the intent
behind it. So, if I'm making a resource
guide for students, that helps Claude
make decisions about using, you know,
analogies and simple explanations and
using examples, and I'd keep that
context when I clean up the skill. But a
long folder listing is something it can
probably look up. So, if the same
instruction is repeated in multiple
different places, I'd check whether I
need all of those copies or if I could
just clean them up. And if a detailed
procedure only applies to when I'm
editing a video, I'd rather load it in
when I'm actually editing a video. And
this is all about getting out of the
model's way, which still means you have
to be clear about what it's allowed to
do. So, I'd keep the claw.md useful as a
starting point. Obviously, telling
Claude things like what the project is
for, giving it any of the gotchas and
the landmines to watch out for and point
it toward the deeper instructions. So,
now my whole video editing process
doesn't need to be there when I'm asking
for help with a script. So, inside Cloud
Code, you can run /docctor to look
through a lot of the stuff happening
locally that you probably don't spend
much time thinking about. Settings,
config files, tedious stuff like that.
So, I ran /docctor in a new session, and
it checks my skills, my memory, my
plugins, my settings, [music] and my
installation. And you can see in this
table right here, it lists each skill,
where it's installed, and how many
recorded uses it has since installation,
and an estimate of the tokens that it's
listing takes up. That basically just
means like the YAML front matter. It
uses that YAML front matter to find the
skill which is different from loading in
the full instruction when it actually
decides to run it and read the whole
thing. For example, agent builder is
estimated at 111 tokens and prove it is
103 tokens and both show zero recorded
uses here. The report flagged 18 older
skills with no recorded use but kept the
ones that I'd only created a few days
ago. So, it's taking their age into
account as well. It also checked 50
recent sessions from this project and
says that it also looked at lifetime
counters across 252 startups and skill
and plug-in dispatches across 223
transcripts. So, I'd still review that
list before I decide to turn anything
off or clean anything up or delete
anything, especially if I do use a skill
through a different tool, for example.
But these are the usage records
available to Claude Code in this audit.
And then it also checks for things like
duplication. So, in mine, the project
map was repeating things already covered
by the routing map. There were also
repeated sections for templates,
references, and archiving files. and it
identified about 2,250 characters of
cuts with an estimated saving of 563
tokens. And you can see it breaks out
different places that memory is actually
coming from. You know, I've got my
project level clouded MD, my userwide
instructions, the automemory index, and
my clawed local MD for instructions
specific to this checkout on my machine.
The local file was just an empty
template estimated at about 35 tokens.
Now, that's obviously not a ton, but the
point I'm trying to make here is that it
will look through a lot of the stuff
that you probably don't even think about
ever. It also found the claw.mmd from
the separate video project in my desktop
folder that loads into Herk 2, which is
roughly another 2,000 tokens just by its
estimate here. So even if you've cleaned
up the file inside your project, there
can be instructions coming from
somewhere else that you don't even know
you're technically paying for. So the
setup checks caught two broken skills as
well. One had the wrong file name. The
other had a formatting problem and its
front matter, the little description
block at the top like we talked about.
So Claude wasn't actually properly
seeing its description. And those files
have been corrected because at the end
of the Doctor audit, it says, "Hey, do
you want me to just fix all this?" It
also looks at things like your
installation. It looks at things like
your automatic updates. And it checked
the settings behind auto mode,
permissions, and my hooks. And real
quick, guys, if you're learning how to
build with AI, I've got a free community
with a bunch of resources and skills and
courses on building AI systems and
agents. And you can also ask questions
and work through the stuff with other
people who are also, you know, behind
you or in front of you. So, if you want
to join, the link is in the description.
Let's get back to the video. All right.
So after running /docctor, I asked
Claude Code to actually look at my
YouTube workflow. And this is the prompt
that I used. I said, "Audit this repo
and show me the smallest change that
would make the path from a raw YouTube
idea to a filming ready script faster.
Use the systems already here. Cite the
exact files you would reuse and do not
edit anything yet." You can see that it
mapped the steps from finding an idea
through research to an outline to a
script and the teleprompter file that I
can actually plug in and read while
filming. Then it looked at how the work
gets passed from one step to the next.
the main recommendations about research.
My outline skill could gather facts, but
it didn't require saving the evidence in
a file that script skill knew how to
check. And my script skill had a hard
rule telling it to verify the facts
again. Now, obviously, I put that there
because I wanted verification. I wanted
to make sure that it wasn't making up
facts or information. But if we've
already found the primary source and
checked what it says, I'd like the next
step to have that work in front of it.
You can see the audit counted 25 video
folders with a script, but only three
with a file specifically called
sources.md. Now, this doesn't mean that
all the other videos had no research,
but it does show that this particular
way of handing over the evidence wasn't
consistent. So, it suggested three edits
across the two existing skills, and I
was able to once again just say, "Yep,
that sounds good. Let's go ahead and
make those changes." So, now that you
understand how you can use Claw to audit
your own setup, I would make this
something that you're doing regularly.
Maybe once a month, you know, if you're
adding a bunch of skills and you're
changing your workflow all the time, or
maybe once a quarter if the setup stays
pretty stable. And honestly, what I
would recommend is every time a new
model drops and you switch into it, you
should probably just run this sort of
audit anyways because every model is
going to interpret your settings and
your skills and your instruction files
just a little bit differently. What's
really cool is once you've done this a
few times and you start to have more
trust in the doctor or in like your
audit prompts, you can start putting
these checks on a schedule. So for this
kind of local setup check, you could use
a local scheduled task [music] that can
see the same files and settings inside
of the cloud desktop app and you can
just leave it open and then you know
once a month it'll run that doctor and
it will run these different audits and
then you can wake up to recommendations
that you can basically just approve or
deny. We've talked a lot about AI oss or
AI second brains and a big pain point
with those is on the humans, right?
Human consistency is the issue.
Sometimes we forget to update things or
we you know put duplicate entries in
there or we forget to delete things,
stuff like that. So, if you can actually
have your AIOS work with you on that
cadence of automating this stuff and
cleaning this stuff, then you're
creating this really powerful sort of
like self-improving, self-cleaning AI
operating system, which is obviously
something that there's a lot of value in
because once you have your own personal
AIOS figured out, then you can start to
figure out how do you have your team
stay synced up and how do you have
everyone working together rather than
everyone duplicating work and building
their own AIOS's. So, anyways, that is
going to do it for this one. I hope that
you guys enjoyed or you learned
something new and if you did, please
give it a like. It helps me out a ton.
And as always, I appreciate you guys
making it to the end of the video, and
I'll see you on the next one.
