---
type: project
description: "So, the CEO of Anthropic just said that the first one person billion-dollar business will be created this year using Claude. He explained the three..."
related: 
last_accessed: 2026-09-20
relevance: 0.97
tier: active
---
So, the CEO of Anthropic just said that
the first one person billion-dollar
business will be created this year using
Claude. He explained the three things
that this business will have, and these
can be implemented by anyone. Even
Instagram's founder said that he could
probably build and run Instagram from
scratch with just Claude and his
co-founder. So, today I'm building a $1
million business using Claude and three
elements that Dario said are required to
be able to pull this off. I'll show you
how I built it, what it does, and how I
made sure that it can run with zero
employees. So, let's get into it. So,
the reason that we're building a
million-dollar business instead of a
billion-dollar one is because a billion
dollars is a great headline, but a
million-dollar business is way more
approachable and realistic for the
average person looking to get started.
Let's start with the three things that
Dario actually talked about. Now, real
quick, Dario didn't publish like an
official three-step checklist. He was
answering a question in an interview
about what a one-person billion-dollar
company could look like. I'm turning the
examples from his answer into three
filters that we can actually use
&gt;&gt; [music]
&gt;&gt; today. So, the first filter is a
business that trades or deploys its own
capital. Dario's example was a
proprietary trading firm. The same
general model could be a real estate
flipping company or even a used car
dealership. The business uses its own
money to buy something, improve it, or
trade it, and hopefully sell it for
more. The benefit here is that you don't
need thousands of customers or a massive
sales team, but you do need money,
expertise, and a willingness to take on
real financial risk. So, for this video,
that filter helped me rule out the
capital heavy route. I wanted something
that a normal person could start without
putting a bunch of their own money at
risk. Now, the second filter is software
because normal people can build useful
software with just Claude code now. And
the options here are basically endless.
You could build software that writes
content or even runs a cybersecurity
audit. But being able to build software
doesn't automatically make it a good
one-person business because you could
still end up with a product that needs
custom onboarding, constant support, and
a salesperson on every single deal. So,
that final filter is that sales and
customer support need to be highly
automated without the experience
becoming terrible for the actual users.
And that filter narrows the list quite a
bit. The offer should be repeatable and
need very little customization, and it
should be easy to start using for the
users without, you know, heavy
regulation or tons of different support
questions. Those types of support
questions need to be able to be answered
by an AI agent. That's why simple
products like a file converter or an ad
reviewer, things like those make sense
cuz the customer understands what
they're buying, they can get the result
quickly, and they don't need like a
custom consultation in order to get
value out of the product. So, the first
filter ruled out a capital-heavy
business. The second led me to software,
and the third narrowed it to a product
that could run without hiring a massive
team. Or, I guess a team at all. Now, I
gave Claude three ideas to compare. One
was a scheduling tool, so something like
Calendly. Another one researched
companies and drafted cold outreach
messages. And the last one stress tested
customer-facing AI agents before a
business actually launched them. So, I
asked Claude to run through all these
different examples, you know, play
devil's advocate, spin up, you know,
like a war room debate panel, and I
asked who would pay for each idea,
whether the result could be delivered by
software, and whether one person could
realistically sell and support [music]
it. So, like the scheduling tool was
very easy to use, but it would be
entering a market full of mature
products. The outreach tool was super
easy to explain. It doesn't prove that
those emails will convert. Now, the
third idea had a much clearer result. A
company connects its AI agent, the
software puts it through difficult
customer situations, and the company
gets a report showing where the agent
failed. So, that's the business that I
decided to build today, and Claude and I
named it Agent Report Card. In simple
language, it's quality assurance
software for AI agents, AI eval
software, essentially. So, an AI agency
might build customer support bots for 10
different clients, and before they hand
one over, they need to know that that AI
agent won't invent a new policy or
refund the wrong person or expose
private data, things like that. So,
basically, what they need to do is have
proof that the AI agent will actually
perform as expected rather than just
going on vibes. And without software,
somebody has to test all of those
conversations manually. And whenever the
agency maybe updates the agent with a
new prompt or a new AI model, its
behavior is going to change. So, Agent
Report Card will run the tests, save the
evidence, help diagnose the failures,
and create a report that the agency can
give to its client. Now, the tool stack
is pretty simple. Claude does the AI
work, Claude Code helped me build the
product, the app stores the test
history, and then Clay helps find
potential customers. And just to be
clear, this business doesn't literally
trade its own capital. That was the
route I used the first filter to
eliminate. It does fit the software
route, and the product is repeatable
enough that sales and routine supports
can be automated around it. And by the
way, you can get everything that I'll
build to start this business for free.
I'll attach the skills, the prompts, and
the frameworks from this video inside of
my free school community. So, if you'd
like to follow along, you can get them
for free by joining with the link in the
description. If you have any doubts or
problems, someone from my team or a
member of the community will help you
out. So, let's get back to the $1
million business. So, I divided the
one-person business into three parts.
First is the actual work the customer is
paying for. Second is the agent that
handles sales and customer support, and
third is the workflow that finds
potential customers and prepares the
outreach messages. So, let's start with
the product. I've connected a customer
support agent to Agent Report Card. And
you guys can see the connection right
here. The app runs that agent through 16
tests. Think of them like mystery
shoppers. Some ask normal questions,
while others try to get the agent to
take a risky action or answer without
enough information. And this is
essentially our golden data set that
we're testing the agent against because
we know what the correct answers should
be or what the correct agent actions
should be. So, the first completed run
right here scored 88. 14 tests passed
and two failed. So, now we can open up
these failures, and we can see the
customer's question, the answer the
agent gave, and why that answer actually
failed. So, this customer here
threatened a billing dispute. So, the
agent should have stopped and send the
conversation to a human, but it didn't
do that clearly enough. I sent that
failed conversation to Claude. Claude's
able to diagnose the problem and suggest
a tighter instruction for billing
disputes. [music] I approved that new
policy version and ran the same 16 tests
again, and the score was still 88. So,
what happened here was the billing
problem was fixed, but a different test
failed because these agents can respond
a little differently from one run to the
next because they're AI agents. They are
non-deterministic. So, fixing just one
example doesn't prove the whole agent is
reliable, which is why in this example
we're doing 16, but realistically, the
bigger the golden data set, the more
confidence you can have in the quality
and performance of these AI agents. So,
anyways, I ran the suite again and this
time the score moved to 94. Both
original failures were fixed, but the
agent still mishandled a request to
export private customer data. So, you
can see exactly what improved and what
still needs work. The app isn't forcing
a perfect score just to make the result
look good. It's helping you diagnose and
fix. Then after all this, I click create
report and this is the actual
deliverable. The client can see the
score, the test that were run, what
changed, and the issue that's still
open. The private conversations and full
prompts stay inside the agency's
workspace and that is the core business
workflow. The customer isn't paying for
the dashboard, they're paying for proof
that their agent was tested before it
reached real users and put their
reputation or their business at risk.
All right, so now part two. Now the
business needs a way to handle new leads
without me taking the same introductory
call all day. So, a potential customer
can submit this trial form. In this
example here, the agency manages 14
agents, still test them all manually,
and has already seen one agent try to
refund the wrong order. So, what Claude
will do here is read what they
submitted, explain whether the company
is a good fit, and recommend a small
trial using its human risk agent. You
can see right here the reason it
qualified the lead it created. And I
still make the final decision before
anything moves forward. So, the
repetitive part of the first sales
conversation is pretty much handled.
Claude doesn't send an email, charge a
card, or promise the customer anything
on its own. Now, customer support works
very similarly. I submitted a normal
question asking how to rerun only the
tests that failed. Claude found the
answer in the product guide and polished
it to the customer support page. So,
then I submitted a request for a refund
and permanent account deletion and what
Claude did is drafted a response and
sent the ticket to me, but it left the
actual refund and deletion completely
untouched. So, routine questions can
keep on moving through while decisions
involving money or customer data,
essentially decisions that are high
risk, still come to the founder. And so,
obviously when I say zero employees,
right now I don't mean that nobody
works. You know, it's it's a one-person
company, one person running the company,
meaning me. But the software handles the
repetitive work and I can handle the
decisions that require judgment and
think about how do I actually grow this
whole operation. Now, the last part,
which is part three, is finding
companies that might actually need this.
So, what I do here is I use clay to find
businesses that are publicly deploying
AI agents. And then Claude checks the
public sources, it explains why that
company might be relevant, and drafts a
message to them based on the evidence.
Now, the reason we're using Clay here is
because it just has the best B2B data
out there. And in order to successfully
do cold outreach, you need to be able to
build a high-quality list of
decision-makers that actually fit your
ICP. You need to be able to enrich those
leads so that you can actually
personalize the messages at scale. And
then you can also schedule all of the
sending inside of Clay as well. This
software will pull data that isn't
accessible with other tools or agents.
So, we're getting the highest-quality
stuff right here. And also, in this
specific example, we did use Claude to
generate the personalized messages based
on the enriched leads, but Clay could
actually do that as well. So, it's
really a one-stop shop. And if you guys
want to check out a deeper dive video
that I did with Clay and Claude Code,
I'll tag that right up here. But
anyways, now if I open up one of these
companies, you guys can see the source
and the message that Claude wrote. And I
can review and approve the draft, but it
stays marked [music] not sent. And that
matters because finding a relevant
company and writing a good message is
not the same as getting a customer. So,
this workflow automates that slow
research and preparation. And the next
real test is obviously sending the
outreach and getting replies, seeing
whether companies will pay, and being
able to customize that actual process
because there's multiple steps in that
cold outreach funnel where clients may
drop off. Now, at 499 bucks per month,
Agent Report Card would need 168 active
customers monthly to pass $1 million in
annual recurring revenue. So, I now have
the product workflow, the sales and
support system, and the client
acquisition workflow that one founder
would need to operate this type of
business. What I don't obviously have
yet here is 168 paying customers. So,
the first milestone is getting five
agencies to connect their own agents,
use the report, and pay for it, and
figure out what type of feedback we get,
and how we need to improve the process.
[music] So, now I would just need to get
very, very clear on what I call the AI
monetization readiness assessment, which
is the three P's: pain, promise, person.
Actually, no, I like to go pain, person,
promise. So, what is the very specific
pain point that you're trying to solve?
What is the exact person that you're
trying to solve that pain for? And how
can you promise that your software is
going to solve that exact pain point for
that exact person. So, for Agent Report
Card, for example, I'd say that the pain
is that agencies are manually testing
customer support agents and can't prove
the quality of them before pushing them
into production. The person is an AI
automation agency who is deploying
customer support agents for their
clients. And the promise is that Agent
Report Card runs your agents through 16
or more high-risk scenarios and shows
you exactly where those agents fail and
creates a client-ready reports on that
evaluation. So, after I read off my
three P's, you might be wondering why
focus specifically on customer support
agents instead of just general AI
agents? Because saying all agents is
very broad. You know, sales agent,
finance agent, sport agent, they all
have different types [music] of tests,
different processes. And if we tried to
cover everything, the product would
become generic and the promise would get
a little bit more vague. It has to be
very specific and strong. And the truth
is here, there are already other
products out there that do evals or QAs
for AI agents. And those other companies
probably already have customers, more
capital, and a reputation. So, customer
support agents gives us a repeatable,
high-risk situation that we can test and
we can get really good at. Things like
refunds, billing, disputes, account
deletion, private data requests, knowing
when to involve a human, you know, those
escalations, things like that. It allows
me and my software to become experts at
the specific process. We can then, if we
need to, later expand into other agents.
But we need to get a good foundation
laid. And starting narrow gives us a
specific customer, a super painful
problem, and a promise that our software
can actually deliver on. And because of
the way that we're looking to start the
pricing, we would need 168 customers to
pay us each monthly to pass $1 million
annually. And that's obviously not going
to happen quick and it's not going to be
super easy, but 168 customers is
realistic in that niche. Okay. So, in
this video, I kind of talked a lot about
a one-person software business. But what
if you wanted to go down the
service-based route, which is actually
what I did? I started out as an AI
freelancer, and then once I passed
around 10K per month just by myself, I
decided to start bringing on developers
and sales people and eventually scaled
the whole operation with some
co-founders as well. So, if you guys do
want to learn more about that road map,
there is a link in the description for
that exact road map. But anyways, that
is going to do it for this one. So, if
you guys enjoyed the video you learned
something new, please give it a like it
helps me out a ton. And as always, I
appreciate you guys making it to the end
of the video and I'll see you on the
next one.
Thanks, everyone.
