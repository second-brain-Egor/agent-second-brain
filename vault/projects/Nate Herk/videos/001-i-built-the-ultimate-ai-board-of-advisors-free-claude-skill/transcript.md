---
type: project
last_accessed: 2026-10-13
relevance: 0.97
tier: active
---
So right here you can see that I've got
Jeff Bezos, Paul Graham, Alex Herozi,
Gary Vee, Dan Martell, Gino Wickman, and
Warren Buffett sitting here in what I
call the roast room. And what's
happening is all of these advisers are
writing their opening positions and then
they're going to have a debate about the
actual question that I submitted to
them. So right here you can see that
this debate is about the Austin Inerson
conference in June 2027 and they have
four different options to choose from. I
gave them A, B, C, or D. And what's
actually going on here is this is linked
to a cloud code session as you can see
right here where I've shot off this
prompt where I basically did a slash
roast room which is the skill that I'm
going to show you guys and give away
today. And I submitted the question with
all this information about the options,
business information, resources, what
would success look like? And now we're
able to actually sit here and watch them
discuss this live. And so obviously this
visual interface is kind of just a fun
visual interface that sits on top of
what's actually going on. And what's
really going on is we're still running
this skill inside of Claude Code where
we have these different personas and
they're going to be discussing this. So
I've done things in the past where I
actually run a slro, but I've made this
a little bit more formal and I've made
this, you know, more formalized personas
and I call this the roast room. Now what
I think is cool is all of these personas
were pulled as inspiration from the
actual people themselves. Jeff Bezos
focuses on one question which is is this
the right bet and how reversible is it?
Paul Graham focuses on one question
which is is this something people
actually want and is it growing? So, all
of these essentially agents or council
members are thinking about one very
specific thing. Warren Buffett is
thinking about what does it do to cash
risk and long-term value. And obviously,
I'm going to break down how I built this
and what actually lives inside of each
of these specialized agents brains
because there's a lot of data that lives
inside of each of these guys' brains.
So, right here you can see they actually
start discussing and there's something
going on with Jeff Bezos because I have
this sort of like minimized so it looks
kind of goofy but we added in these
little animations so we can actually see
them talking. They're going to give
their opinion on what options. So you
can see Jeff Bezos came in with a B and
he scored them. So he gave B seven out
of 10 and we can see why. We can also
see that Paul just went with B and he
gave it a 6 out of 10. Hermosi is also
running B and gave it an 8 out of 10. So
this is basically how the council works.
They're going to go through in one round
and then debate and then they're going
to go through in another round and then
debate and they'll come back to us at
the end with a final vote and verdict.
And I can go ahead and speed this up
because all of these decisions have
already been made. This is just like I
said the visual interface. But in this
case, you can see that all seven of our
adviserss here voted B and they scored
it an average of 7.1 out of 10. So now
what they're going to do is they're
going to read through each other's
positions and they're going to fire
back. In this example, they're pretty in
line already. But it's really
interesting when they don't actually
agree and they have to try to persuade
each other on why their decision is a
better decision. And because I have
cloud code open on the left, we can see
what's actually being facilitated. This
is sub agents. It's not an agent team.
So that means that each sub aent is
basically talking to a chair and the
chair is facilitating the debate. So
right here it says all seven seats in
round one backed a gated B which means
the chair treats as a warning. So round
two is asking Buffett and Martell to
argue for option C as hard as they can.
And then we're going to see how they
think about that and then we'll see what
the other founder council members think
about as well. And now you can see how
they're sort of like starting to make
these connections between each other.
They're arguing with people or they're
agreeing with people. So Gary Vee right
now is talking to Buffett. Dan Martell
is saying something about Gary Vee and
they all start to actually come together
now and hopefully they're trying to get
to an overall roast room consensus. And
as this is happening, you can sort of go
through and you can see the key points.
You can see what round one looked like.
You can see what round two looked like.
And you can more specifically see what
Bezos said to Gary Vee. You can read
through it here. You see, you have
things like, I disagree with this. I can
see it here. Blah blah blah. Here's my
stance. And you can look through all of
the stuff. This is what Hermoszi was
saying to Bezos. But now we're moving on
to the final round, round three, which
is the actual vote. And it looks like
it's going to come back and it's going
to be to go with option B. But we will
see. And there you go. You can see that
they're starting to come in with their
final votes. And what's going to happen
after is we are going to be delivered a
final verdict that we can sort of read
through and see like the key decisions
and the key points that were made. So
you don't have to like watch this whole
thing. Usually what I'll do is I'll
shoot off a couple prompts. I'll come
back and then I'll just read through the
verdicts. And it really helps me make
decisions. And I don't always just
blindly take whatever the council gives
me. But what's helpful is to read
through each of the decisions and and
read through the perspectives because
sometimes that helps me just think about
it in a different way even if I don't
actually go with their opinion. So this
was basically the final verdict. It was
to go with conditions run B as a $3,000
annual plus Austin tier capped at 120
seats and sign nothing until 50 members
have paid 150,000 by January 15th. And
what we can do is we can actually
download this as a PDF. So, if I
download this and I open this up, you
can see that we get this PDF with our
scores and with all of this information
on each round, what they weighed it, and
how we can sort of like take this, send
it to our team or make a decision,
whatever we need to do with it. So, that
was an example of what this looks like
and the deliverable. I'm going to break
down how exactly this works, but first,
I want to show you how you can get it
for completely free. You're going to go
to my free school community. It's linked
in the description. You're going to come
in here, go to classroom, and click on
AI skills. and there will be a link in
there that takes you to the full repo
for this roast room setup. So that is
what the interface is like. You can see
that if I click on past sessions, I can
actually look at all the different PDFs
that has been created from this roast or
so from the roast room. And we could
also actually replay the council. So if
I went to this first sales hire or keep
selling, it will go ahead and basically
replay this whole thing for me, which is
pretty cool. And what's interesting is
sometimes the actual prompt that you use
to shoot off for the roast, it might not
use all of the personas here. If it
realizes that, oh, we only really need
to hear from Buffett and Martell in this
specific example, then it will only run
Buffett and Martell. The one that we
just did utilize all seven. So that was
great. But this specific council, as you
can see about first sales, hire, or keep
selling, it only had to talk to Graham,
Hermosi, Martell, and Buffett. By the
way, guys, I've got this completely free
SOP for you about getting your first
aation client. It's going to go over the
exact steps that has been proven for
hundreds of our AIS Plus members to get
their first paid gigs. It goes over the
one sentence service pitch that can get
you started today. Why your first client
should cost you money. The 5-minute
video that answers, can this person
actually deliver before you've actually
received any money. What to do when you
have zero case studies. There's so many
good things in here that are going to
help you out. Even if you already do
have clients, I would recommend grabbing
this because like I said, it's yours
completely free. So, if you want to grab
this, there's a link for it down in the
description. Let's get back to the
video. So what this means is it stores
all of your sessions. So if I come back
in here and I go to claude code and I
open up the files. If I go to my
projects and I haven't renamed this yet.
I used to call this founder council but
I can go to my founder council. I can go
to my sessions and I can see these
different sessions that I had run and
then I can actually investigate them and
look at the brief. I can look at each
round. And that's basically what we're
seeing in this interface. We're just
seeing it in a nice pretty way. But of
course you don't need the interface. You
could just run these founder council or
these roast room sessions without the
interface. But I thought the interface
was a nice touch. But let's talk a
little bit more about how this actually
works because I think it's super super
interesting. So what we have is the
roast room. So that's basically us and
Claude Code is essentially a chair. It's
the facilitator of the roast room. We
have seven advisers like I showed you
guys in the actual demo. And what
happens is each of these is their own
sub agent. It goes through three rounds
where they write their opening position.
Then they look at each other's
positions. And then the chair
facilitates, hey, you argue with him,
you argue with him. And then they go
through on round three and they vote and
then everything is saved and we get a
final verdict PDF. Now, the reason I
wanted to use sub agents is because that
way we could have one chair
facilitating. It's also cheaper than if
we ran this as agent teams. I used to
run the roasts as agent teams, but I
switched back to sub agents because I
just found that the agent teams and the
sub aents didn't really give me
different answers. They were giving me
very similar answers and sub aents were
cheaper and they felt more like I was
able to keep the actual real voice of
whoever I was creating. It just felt
more organized. So these are all their
own individual sub aents and I will show
you guys what those sub agents look like
in a sec because like I said we scraped
through a ton of data to make these. So
what that looks like is for example Alex
Herozi is focused on offer pricing and
sales. We have an actual agent file. So
it's a sub agent file that gets called
in the skill and it says hey you're
going to you know spin up this Alex
Herozi council agent. This file
basically contains the way he thinks who
he is the question he owns and how he
answers how he makes decisions. And it
also links to all these other files that
are basically his brain. So the eight
rules he decides by his named
frameworks, principles, positions,
stories, voice, and sources. And all of
this was just scraped from public stuff
that he's put out there, YouTube videos,
exosts, LinkedIn posts, blogs, things
like that. You can see in this specific
example, we went through about 124
sources, over 1.3 million words, and we
put that into his brain. So, we did that
six more times with all of these other
members of the actual council as you can
see right here. And the cool thing is if
you wanted to maybe swap out like Dan
Martell and swap it in for someone else
based on your industry or based on your
use case, then you could basically just
run the same thing. You say, "Hey, you
see how these seven advisors are set up?
I want you to build me another one
that's just like him, but let's build
this one for um you know, Barack Obama.
I don't know, whoever you want it to
be." And then they go through and they
actually score every option. They wait
it by relevance and then that's sort of
what's debated on. So when you actually
come in here and you clone this repo,
you'll basically just give your agent
the link to this and then you'll be able
to just say, "Hey, install this and it
will put it into your project or you
could create a new project for it if
you'd like. Now, what's cool is let me
open up thiscloud folder to show you
what these agents look like. So in the
cloud we have agents and here's where
you can see we have our council Bezos
with the brain and how you talk, how you
debate. We have Buffett, we have Gary
Vee, we have Hermosi, Martell, and
Wickman. We've got all of them right in
here as sub aent files. And you can see
the sub engine files are not that long,
but what happens is we're routing it to
the brain. So we're saying, hey, you can
read your hot MD and then you can look
in your frameworks or your positions or
all of these things when you need to
make decisions. And so what that looks
like if I open up our skills right here,
you can see that we have these things
called brains. So in the brains, we have
Hermosi, Martell, we have all these
people, right? So for example, let me
just open up the Hermosi brain. We have
the hot, which is basically his hot
sheet, which is the eight rules he
decides by. We've also got some
frameworks here like value equation and
grand slam. We've got money model and
client finance acquisition. These are
all things that he talks about a lot if
you've read his books or if you watch
his YouTube videos, stuff like that.
Decision loop, signature questions, etc.
We also have information about his
books. We have frameworks, we have
positions, we have sources, we have
stories, stories that he has told, which
is really, really interesting and it
makes it feel more personal. And then of
course, like I said, we've done the same
thing with these other brains. So if we
look at Jeff Bezos real quick, same
thing. We have the hot goes over his
worldview, eight rules he decides by. We
have his positions on certain things. We
have his sources. We have his stories as
well. All of these are just a bunch of
different markdown files that were
scraped and created by having a bunch of
agents go do research on these different
people. And now we have this framework
of, okay, if I wanted to add another
person to our council, here's how we do
it. So, it's really, really a simple
setup, guys. And like I said, the visual
interface I showed you in here, purely
visual. You don't actually need this.
The skill will do all of the same stuff.
It'll still generate the report for you.
It will do all of that. But if you want
to watch it, then you can watch it in
here. And the last thing really that I
wanted to talk about here is how to
actually create a good question for your
console. There is obviously the idea of
building a good question, but then
there's also like the context. So, of
course, when I'm asking it questions in
here, it knows everything because it's
already in my AIOS, which means if it
has other questions, not only can it ask
me because if it doesn't feel like it
knows enough to send it off to the
council, Cloud Code will ask you, hey,
in order to send it off, let me ask you
this question, this question, and this
question, but if you have your AIOS set
up correctly and you have all your
connections and you've got your own
personal context and stories and meeting
transcripts and whatever it is already
loaded into Cloud Code or Cloud Code has
the ability to touch those, then it will
actually go pull that data and it will
help the council make an even better
decision because all that context
already exists. So, what do you actually
want to give it when you're asking a
question? Give it the decision. This is
what I want you to tell me. Give it
options. Giving it two or three options
at least is better. Otherwise, it's sort
of hard to like categorize what
potential paths you could go down. And
it may even be more overwhelming because
then you might feel like, oh, I actually
have seven paths because each persona
gave me a different option. But in
reality, maybe all seven are saying some
combination of like option B. So, give
them options, give them real numbers.
So, if you feel comfortable telling them
like revenue and team size and and
things like that that contextualize this
that are really important to actually
making a decision, give that
information. Give it limits like
deadlines, hours, and budgets. Give it
what success looks like. This one's so
important. You have to give it context
on why do I need this decision? What
does good look like? And how do I get
there? How should I be thinking about
that? And then, of course, which way
you're currently leaning and why?
Because, as we know, sometimes AI likes
to agree with you. But this roast room
is basically set up to make sure that
it's not just agreeing with you and
maybe it's going to convince you the
opposite or maybe it's going to validate
you, but it's not just going to blindly
do that because they all have their own
principles and they all have their own
way that they think about things. And of
course, it should be very, very simple.
Once you get into this interface, you
can click on what to put in your
question and you can look through this.
You can also say, "Hey Claude Code, look
at the roast room and help me turn this
into a good roast room prompt." And then
you just talk for a little bit and it
will turn that into a prompt and you can
shoot it back in. And then you basically
just run the skill and the visual
interface will pop up and start running
through all three of those rounds. So
anyways guys, I know that this is a very
simple skill honestly like a very simple
walkthrough of the skill and how it
works and what it does, but it is
something that I do use a lot and it's
something that I think that you should
all get in the habit of. It's a really
important idea of being able to sort of
outsource your thinking but not the
understanding and be able to leverage
other people's subject matter expertise
because at the end of the day we're all
human and we all have subject matter
expertise in a few domains but we won't
be able to have subject matter expertise
in every single domain possible. But
what you can do is you can use agents to
go store some of this knowledge. So
let's say you're building an app in
cloud code and you don't really know
that much about security. What you could
do is you could build a security agent
and you would say, "Hey, go research
everything there is to know about
security. Go read these articles. Go
read these books. Go watch YouTube
videos and store all of your knowledge
in a skill or in, you know, your agent
brain." And then if I have any security
questions, I can just ask you. And it's
just about building all these little
specialized agents and outsourcing the
thinking, but making sure when they come
back with, hey, based on my findings,
based on my research, here's what I'm
recommending. You still need to take
that recommendation, process it,
understand it, and don't just blindly
accept what what it comes back with. But
building specialized people like this
really helps you feel more confident in
the answers you get back, especially
when you have them debate each other.
You could have a, you know, a security
agent and you could have like a CTO
agent and you could have them discuss
things and bring that verdict back to
you. So, it's all about figuring out how
can you leverage other agents and other
perspectives to help you make a
decision. But like I said guys, you can
find that for completely free inside of
my free school community. But that is
going to do it for today. If you guys
enjoyed the video or you learned
something new, please give it a like.
Helps me out a ton. And as always, I
appreciate you guys making it to the end
of the video. And I will see you all in
the next one. Thanks everyone.
