So, I just had Fable 5.1 and Fable 5
build me the exact same app, and it
wasn't even close. Not only did these
apps look and feel very different, but
one cost me 1,200 bucks, and one cost me
500 bucks. One worked for a day and a
half, one worked for just half a day.
So, today I'm going to be breaking all
of this down for you guys. So, let's not
waste any time and just get straight
into the video. All right, so I thought
that I would start with the prompt that
I gave these two agents. Now, this was a
big/goal prompt. Please don't roast my
prompting. But, I gave them both the
exact same prompt. The only difference
is that this one said you are Fable 5.1
and you work inside of this folder
whereas the other one said you are Fable
5 and you work inside of this folder.
That's the only difference. Everything
else word for word the exact same. And
I'm going to show you guys how
interesting it is because they
interpreted it so differently. But
here's something that I think is key. I
didn't have Fable 5.1 build the entire
app and Fable 5 build their entire app.
I wanted them to basically delegate
everything. I said you own strategy,
planning, delegation, sequencing,
quality standards, and final acceptance.
Do not personally perform engineering
research, debugging, testing, or visual
design production. Preserve your context
by delegating execution through dynamic
workflows. Primarily use opus workers
for architecture, product and design
direction, difficult problem solving,
and independent reviews. Primarily use
sonnet workers for implementation,
research, testing, debugging, and
iteration. Give workers clear ownership,
prevent conflicting edits, and replace
or redirect workers when results are
weak. Worker failure is still your
responsibility. So, I'm not going to
read this entire prompt, but this is
kind of the gist of it. I gave it
bullets on the required product and I
gave it the definition of done and I
told it to not stop at a plausible
implementation but continue
orchestrating until you have objective
evidence that the complete product works
and is presentation ready. So
essentially what these agents are
building is they are building ops flow
which is a local first visual automation
studio for designing and simulating
incident response workflows. So it's not
an workflow automation platform like
nen. It is just meant to visually show
and kind of like rehearse. It's for the
person who owns what happens when
production breaks. So, in layman terms,
it lets you draw your emergency plan as
a flowchart and then you can actually
visually watch how that plays out. So,
now that that boring stuff is out of the
way, let's take a look at the actual
apps that they built. Okay, so here is
the first one. I'm not going to tell you
who made this one yet. I want you guys
to try to form your own opinions and
then I'll reveal that after we look at
both of them. But this is what we're
looking at. This is the UI. The first
thing I'm thinking about is, is this
overwhelming? I am just starting to look
at this. I've never ran either of these,
but I'm just taking a look now. And
let's see what we've got. So, we've got
triggers on the lefth hand side. We have
trigger, condition, action, approval,
resolution. We can drag them into the
canvas here, and we can hopefully start
to connect them into things. Okay, that
looks seems like it works good. We can
connect the trigger into this section
over here. Okay, so so far the UI is
responsive and I can use this. Let's
see. Can I close this? Okay, there we
go. So this is kind of nodebased
workflow but it is vertical rather than
horizontal. So what I'm going to do is
see if I can delete that connection.
Delete this connection. Delete that.
Okay. So let's go ahead and run this. So
I'm just going to click run right here.
We can visually see the stuff happening.
That's pretty cool. We're seeing this
stuff being processed. And now what do
we get at the end? We have a completed
run and we're basically able to see what
happened. Can I move this up? So I'm I'm
not able to expand this. I think that
what you should be able to do is grab
here and drag this up so you could look
at this full screen because this is a
little bit hard to actually look at
right here. So there was three that got
skipped in this branch and there was
seven that got executed. The resolution
was mitigated by roll back. Okay, run
has been completed. Okay, awesome. So
that's kind of how this one flowed. This
seems to work just fine. We cannot zoom
in on that. If we want to zoom in on
this thing, oops, sorry guys. We have to
go like this, but then we can navigate
from there. Okay, so far so good. Let's
go into the other version now. So, this
is what the other one looks like. This
is the UI. If you think it's better, if
you think it's worse, I personally think
that this UI is a little bit better
because I don't know if you guys have
realized this sort of card where you've
got like the rounded crop color that is
just that that screams AI generated to
me. Now, I'm not saying this looks like
AI slop, but it that screams AI
generated. Whereas over here, this
doesn't look as bad. Like, I think that
this looks a little bit more clean.
Let's see if I can drag something in.
Okay. And I like how it did me a little
zoom right there. Let's see how I Oh,
that's a resolution block. So, that's
not going to let us connect anything.
Let's do another, I guess, condition
since that's what we did in the other
one. We can grab the trigger, route it
to there, or can we not?
Okay. Uh, connection refused. API error
spike detected. Already has an ongoing
connection. Okay. So, one trigger only
lets you connect to one thing in this
version as you can see. So, that's
interesting to note. We can connect that
back in there. I can drag this and
connect to there. I can drag this and
connect to there. And that gives us a
false branch. Okay, cool. So that works
as expected. Let me delete these. We can
zoom in down there. And I can move this
around. So everything over here as well.
Seems pretty responsive. Can we move
this up? Aha. So in this one, you can
expand this a little bit. You can also
make this part. Oh, you can kind of zoom
that in. And we can also close this tab
if we want to. Okay, cool. So let's go
ahead and give this version a quick run.
I see the run in the top right. I also
noticed that we can go on light mode
here. So sorry if I just blinded
anybody, but let's go ahead and do a
run. So we see visual processing here as
well. We can see this node is waiting.
It's waiting for approval here. So
approve production roll back needs sign
off from this email. Waiting for
decision. I'm going to go ahead and
approve real quick and see what happens.
It goes down the path. Okay, cool. I'm
going to run that again and see what
happens if I decline that. I'm going to
reject. Okay, it just goes ahead and
stops. But now, if you guys notice it,
it keeps going down the true path. So,
I'm trying to look how do I actually
change that? Um, oh, I can view the node
by the way that that errored. But if I
go to the payload, I can choose minor
degradation and hit run again. And now
it goes down to false. Okay, so that's
cool. That's cool. If I click into a
node, by the way, on the right hand
side, we can have a label, we have the
action type, we have the target, and we
have all this information to configure
it. And similarly on this one, when you
click on a node, you get all of that
information over here to tweak, I guess.
Okay, so I do like the UI of this one
better. So, what I want to do real quick
is paste in different workflows so we
can just see how they look. But I wanted
to reveal this one is Fable 5 and this
one is Fable 5.1. So, we'll get into how
much they cost and which one I think is
the winner overall. But just wanted to
tell you guys this is Fable 5, this is
Fable 5.1. And what's really interesting
to me is that they accept different
schema for the way that we upload new
workflows. So if I delete this and I
want to import a workflow from JSON,
this schema, which now works in here, if
I try to import that into this version,
doesn't work. There's nothing on the
canvas. So I don't know why, but they
decided to build it in a way that's
different. But anyways, I imported this.
Let's just go ahead and run this real
quick to see what this looks like to
process a much larger workflow. There's
different paths. I'll go ahead and
improve this. I do think that this one
visually, it does look good. I like the
way that this feels and looks as we go
through the automation. Oh, wait. I that
was waiting on me again. We'll go ahead
and approve. So, anyways, that seems to
all be working as expected. This is an
action. Cool. Okay. Now, let's go over
to the other version and let me paste in
this prompt. Go ahead and get that in
there. Import. Okay, cool. So, now we
have another one. I will say
I honestly think that Fable 5 looks
better when you're zoomed out because
the text doesn't grow. You see here as I
zoom in and out it stays consistent.
press here. This looks I think this
looks very cheap for this to be getting
larger. I think it looks cheap. I I
guess that's a preference thing. Some
might disagree, but I think it looks
cheap to be like that. So, anyways, let
us continue going down this branch just
to make sure everything looks good.
Overall though,
I just overall like the UI of this one a
little bit better except for that zoom
thing. I don't love that at all. Okay,
cool. So, this is done. Now, let's talk
about some results stuff. So, what I did
next is I had Codeex open these two up
and I didn't tell which was which.
That's why in this chart it says port
4382 and port 5321. And I said, "Hey, I
gave these two agents the same prompt
and here's what they built. Test the
heck out of them. Tell me what you like
about each one better." Overall, you can
see the weighted score is that Fable 5.1
got a 9.1 and Fable 5 got an 8.4. So, it
looked at visual design and hierarchy,
Fable 5.11. First run ease of use 5.11
workflow authoring you can see here dry
run experience fable 5.1 and workflow
authoring as well as validation and
safety which is important but very very
close and then fable 5.1 ultimately like
I said one by seven points or.7 points
and after looking at this testing them
and having codeex review this is kind of
the chart of what they thought was
better about each one fable 5 had deeper
authoring controls
clear autosave timestamp. It included
useful negative test presets like
missing severity, excellent live preview
against the current payload. I think
that that is very true. Whereas 5.1 had
stronger information hierarchy and more
readable canvas. I do think that that is
true as well, except for when you zoom
out. Strong run summaries and
downloadable run logs, clear visual
states for succeeded, failed, skipped,
and waiting. Rejection currently fails
the run instead of falsely claiming
mitigation. So anyways, that is a little
bit of differentiation here. Let's talk
about the cost. Okay, so I think this is
super interesting because 5.1 cost a
little over double of what Fable 5 cost
and it also took about three times as
long which I honestly was not expecting.
On top of that, what I think is really
really interesting is look at the
breakdown of models here. 5.1 used opus
for about 57% of the work, Sonnet for
about 40% of the work and itself was
only about 3% of the total work/tokens.
Whereas on this side, Fable 5 used
Sonnet for 80% of things, which maybe is
why some of the stuff is so much cheaper
and was quicker, but also a little bit
worse in some cases. But I'm not
convinced that this one was $600
worse. And what I mean by that is if I
spent, what would it be? Like, you know,
700 bucks more on this one to improve it
just to get where this one currently
sits. I think that this one would be
better, which is the one that Fable 5
built. And keep in mind with the
majority of the workers here being
Sonnet and then 12% being Opus and 7%
being Fable 5, I thought that was
extremely interesting. I was not
expecting that. Do you know what I mean?
Like I think it's good to try to find
some sort of baseline. And the baseline
for me would be if I spent the exact
same amount of money on each of these
models, where would we be? And so if
Fable 5.1 only or like if this workflow
only spent 519 bucks, we probably
wouldn't have gotten something this
good. You know what I mean? So that is
why I am trying to, you know, I'm making
that justification there. Look at the
tokens too on the input. Fable 5, I I
don't know. I don't really don't know if
this is real. I don't know if there's
any way that Fable 5 only took in 256
tokens. So maybe something's a little
bit off there. But when you look at the
output tokens, this seems to make sense.
Now, I think because a lot of this were,
you know, dynamic workflows, sub
workflows, things like that. But, you
know, it's clear that Fable 5 took much
longer and cost about double, a little
over double, 700 bucks more than Fable
5. And if we take a quick look at the
actual context window from these
sessions, here's the Fable 5.1 that was
running on local host 5321 as you can
see. And if I go into here, it only used
404,000 of this context window. So, this
ran for, like I said, a day and a half,
36 hours, and it only used a little
under, you know, 40% of the context
window. If I go to Fable 5, you can see
this one was running on 4382 and this
one used 260,000.
So 26% of the context window. So I just
wanted to show you guys what that
actually looks like in the desktop app.
When we look at the actual pricing
numbers that I just showed you, this
honestly leads me to conclude that I
think Fable 5 won this challenge. I'm
not saying I think Fable 5 is a better
model. I've had a lot of success playing
with 5.1. And I will be honest, when I'm
doing a lot of my general knowledge work
and I'm driving my day-to-day, I do
notice Fable 5.1 being more efficient
and just feeling like it understands my
intent a little bit better. So overall
right now, I like Fable 5.1 a little bit
more. But in this scenario, Fable 5, I
think definitely wins. When you look at
the cost, the time, the efficiency, and
the actual end result, I think that
these apps at the end of the day are
pretty similar. And for 700 bucks, like
would you pay 700 bucks more for this? I
don't think so. But anyways, that is
what I got for you guys today. That's
what I found. I really hope you found it
insightful. But if you want to see how I
use Fable 5.1 to design websites,
specifically things like my Amation
Society site, which I think is just
absolutely beautiful, and my personal
site and a lot of different styles of
websites that have these really premium
animations and just scroll elements,
then definitely check out this video
right here. I hope to see you guys over
there. And yeah, thanks for making it to
the end of this one. See us.
