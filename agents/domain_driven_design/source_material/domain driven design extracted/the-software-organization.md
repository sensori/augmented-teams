# The Software Organization

As organizations consider how to provide better value in the face of
complexity, they often turn to software to deliver more and more ser-
vices to their customers. It's a plain fact that software is eating the
world. Digitizing customer experiences, automating back-office pro-
cesses, marshaling information into insight and even real knowl-
edge—all are driven by software. Software allows us to operate in a
world of automated service that can interconnect with each other to
bring about an era of mass customization. Paradoxically, the era of the
knowledge worker and the human-based organization is being made
possible by our advancements in the machine.

Because of the pervasiveness of software systems in the modern
organization, no serious book on organizational design can be consid-
ered complete without a real look at the synergistic effects that organi-
zational design and software system architecture have on each other.
Too many organizations ignore the impact that organizational struc-
ture has on software design and vice versa, to their detriment. Many
organizations that have truly scaled for agility have done so with scant
attention to published Agile methodologies. Think the Amazons,
Googles, and Netflixes of the world. What these organizations have
done is treat their software and their organizations as a single sys-
tem. They organize around the software they want to create, with the
knowledge that they will write software according to how they are
organized.
This chapter will lay out some of the theory and approaches you
can take to align the two systems of software and organizational
structure. Much of this chapter is taken from my experience in ap-
plying concepts taken from the excellent book by Eric Evans titled
Domain-Driven Design: Tackling Complexity in the Heart of Software.
The book is known for its excellent treatise on how to build software
that mirrors the language of the business. But the book is more than
that. Domain-Driven Design discusses how models of software relate,
integrate, and depend on the teams that build and run them.
When I originally planned to write this chapter, I expected to
have to do a fair amount of work taking many of my experiences and
approaches and refining them to something a little more concise
and shareable. Then I came across a recently published book, Team
Topologies: Organizing Business and Technology Teams for Fast Flow,
by Matthew Skelton and Manuel Pais. This book has some glaring sim-
ilarities to mine in that it covers team and interaction patterns to scale
with agility. Amazingly, we have come to some very similar solutions,
and we even happen to use the exact same terminology in a few places
(we both use the enablement concept). There are some differences, of
course, but conceptually I feel the books are very aligned.
Team Topologies does an amazing job of laying out how to apply
the concept of domains to align team structure with software system
structure. Rather than reinventing the wheel, I’ll be leveraging some
of their work. A big shout-out to the great work Skelton and Pais have
done to move this body of work is warranted. It certainly made writing
this chapter easier.
THE PERIL OF IGNORING CONWAY’S LAW
Let’s start with a discussion on Conway’s Law. Way back in 1960, Mel
Conway observed that when separate groups in a larger organization
worked together on larger systems, they would tend to break up sys-
tems they were working on into parts so that each group could work
on their own piece as independently as possible. Or to quote Conway:
222 ORGANIZING TOWARD AGILITY
“Any organization that designs a system will inevitably produce a de-
sign whose structure is a copy of the organization’s communication
structure.”
When Mel came up with this law, he defined a system more
broadly than just software systems, but it is in the world of software
that Conway’s Law has gained real prominence. Open-source advocate
Eric S. Raymond and software celebrity James Coplien are among the
many that have observed the impact of Conway’s Law on software sys-
tems. James Coplien stated in his 2004 book, Organizational Patterns
of Agile Software Development, that when organizing structures (for
instance, teams, departments, or subdivisions) do not closely reflect a
product’s essentials, and the relationships between organizing struc-
tures do not reflect the relationships between product parts, then
trouble ensues . . .
Over the past two decades of experience in the software world, I
have witnessed the dysfunction that takes place when we ignore the
impact of Conway’s Law. I’ve seen countless teams developing redun-
dant code in the same system that provides the exact same business
functionality, but inconsistently so. I’ve seen teams dramatically in-
creasing code complexity through multiple translation layers design
so that each team can avoid “infecting” their code with another team’s
code. I’ve come across dependency “magnets” that result in multiple
teams being unable to develop or test any functionality without in-
volvement from every other team.
Skelton and Pais, in their book Team Topologies, rightly point out
that when you design a dependency between two parts of a software
system, you also need to think about the ideal communication path
for the two teams in the organization that build or own those parts
of the software system. When the overall organization is small, this
is not much of a concern, but as you scale the number of teams that
are building software, you create real fragility when team boundaries
and module boundaries are inconsistent with each other. Team com-
munication grows exponentially, and the need for management-style
coordination, and even control, goes up.
Perhaps one of the biggest sins we see when organizations don’t
pay attention to Conway’s Law is the creation of the monolith. When
communication is poor across multiple teams working on the same
THE SOFTWARE ORGANIZATION 223
software system, we end up with overlapping modules, poor abstrac-
tions, leaky interfaces, and dependency magnets. Despite the best in-
tention or well-thought-out design, over time our software solutions
devolve into a mess.
When multiple teams do duplicative yet often incompatible work,
they lose the ability to make decisions without input from every other
team. Or worse, they make decisions on their own that negatively im-
pact other teams. They lose the ability to change the system without
impacting everyone else. Monoliths aren’t all accidental: indeed, an
industrial organizational mindset, with its emphasis on standards, in-
structions, and conformity, naturally leads to what Skelton and Pais
describe as monolithic thinking, which is a:
“one size fits all” thinking for teams that leads to unnec-
essary restrictions on technology and implementation
approaches between teams. Standardizing everything
in order to minimize variation simplifies the manage-
ment oversight of engineering teams, but it comes at a
high premium.
If we accept that the wrong organizing structure will have severe
impacts on our software architecture, which in turn will impede our
organization from effectively delivering value using that software,
then it becomes fairly obvious that you can’t design an effective orga-
nizing structure without a deep understanding of software systems. If
you leave organizational design in the hands of your HR department,
then HR will also (accidentally) decide your software architecture.
you want the opposite to occur: you want your architects, senior de-
velopers, or whatever you call your people with deep software system
knowledge to intentionally define teams around the software architec-
ture you have or want to have.
This approach, dubbed the “Inverse Conway Maneuver” by Skelton
and Pais, is an intentional act of reconfiguring the team intercommu-
nication according to the boundaries we want between the different
parts of our systems. The frequency, intimacy, and bandwidth of com-
munication paths shape the kinds of solutions we devise. When one
or two teams closely collaborate on a system, we are more likely to
224 ORGANIZING TOWARD AGILITY
see chatty module boundaries (distinct software modules that send
too many fine-grained methods to each other) or perhaps a system
with few distinct partitions. When multiple teams “intentionally” op-
erate more independently, we are more likely to see the team integrate
through well-defined APIs or to be loosely coupled through publish-
ing and consuming events. When we have a mismatch between teams
and separate system parts, we get a mess. But the idea here, according
to Skelton and Pais, is to use the synergy between the system and the
organization “to our strategic advantage. If we want to discourage cer-
tain kinds of designs . . . we can reshape the organization to avoid this.”
THE PERILS OF FOCUSING ON SOFTWARE INTERNALS
Historically, we have seen an emphasis on focusing software architec-
ture on system internals, decoupling the technology layers as much
as possible in an attempt to create a layered, or “tiered,” architecture.
Systems were divided into a minimum of three loosely coupled layers:
the presentation, business logic, and data layers. Often additional in-
tegration, orchestration, or workflow layers were added to the mix. In
an attempt to follow Conway’s Law, we would create separate teams to
develop and possibly maintain the distinct software for each specific
layer of the system. We ended up with a presentation layer team, a
business logic team, and a data team. Sometimes more than that.
This approach seemed sound to many at the time, but really it is
the product of the inward-focused thinking we see from an industrial
mindset. We saw many of the same problems that we do from a func-
tionally siloed industrial organization. This is because most system
software changes typically impact multiple layers of a software solu-
tion. For instance, if we need to expand our shopping cart function-
ality to accommodate discounts from external marketing campaigns,
that will impact the presentation layer, the business logic layer, and the
data layer. Members from all three teams will need to closely commu-
nicate to make sure that the changes that take place across the system
are consistent and do not contradict each other.
In contrast, when we ask the teams to make changes to how the
solution manages product inventory, we would want that change to
THE SOFTWARE ORGANIZATION 225
have low to little impact on adjacent functions, such as how we manage
customers or perform billing. But in our current organizational de-
sign, concepts such as customers, billing, and inventory are all worked
on by the same teams. Whether intentional or not, we are more likely
to have chatty interfaces and poor partitioning across these functions,
and unforeseen dependencies between these concepts are likely.
Stephanie Dimovski was one of the product owners leading an am-
bitious initiative to modernize the point-of-sales system being used by
in-store pharmacists. She described the problems she faced this way:
Inconsistency in prescription, disbursement, and pa-
tient data had been shown to be costing actual lives, so
it was important to increase timeliness and accuracy
of information across all pharmacies in all provinces
across Canada. We had an immediate focus on build-
ing real-time integration between the store points of
sale and the Alberta health patient and prescription
tracking system. Because of the focus on safety, our
engagement had some pretty tight timelines. Previous
teams on this program had suffered from some previ-
ous hiccups, late delivery, missed scope, things like that.
That put this engagement in a situation where we were
asked to deliver something in a matter of months.
Early on in the engagement, the decision was made
to restructure the teams in our “mission” [their word for
ecosystem] according to architectural layers so that we
could focus engineers on individual components that
they would be experts in. While the product owners felt
there was a risk that teams would lose the context of
the feature as it traveled across the front-end and back-
end teams, we agreed to try it out with an open mind.
In the end, the approach did not provide the gains
that leadership had hoped for. Teams did indeed lose
context as a feature traveled across teams and many
handoffs occurred. Teams did not have ownership of a
feature and therefore didn’t need to be accountable to
the end state of that feature. Really it was a bit of a
226 ORGANIZING TOWARD AGILITY
disaster. The deliver-by-contract approach may have
sounded good on paper, but it required so much up-
front design to understand who could work on what. It
quickly became a nightmare to know who was respon-
sible for which pieces. No one had ownership of when
an end-to-end piece was going to be done. There was
no tangible business “thing” you were building. And our
throughput plummeted, to about seven stories a sprint
from an average of sixteen.
INTRODUCING DOMAIN-DRIVEN DESIGN
Domain-driven design (DDD for short) is based on the idea that the
structure of our software systems should reflect the way business
experts think about their business. Software should mirror business
concepts and subjects, business activities, business state, and business
rules. Infrastructural and cross-cutting concerns should be treated as
they are, which is as system internals.
In a domain-driven design approach, you partition modules first by
business concepts, known as business domains. Things like customers,
billing, orders, and fulfillment are all potential ways to partition the
system. As systems scale, the rate and reasons to introduce change are
more likely to be different across these business domains than across
software layers. For instance, changes to your supplier code will likely
change the way your fulfillment code works but have little impact on
the code you use to acquire new customers.
In contrast, UI, workflow, and data access are considered to be
internals, and while consistency may be desirable for these pieces, it
is far more important to have well-managed interfaces between the
business-oriented concepts than to obsess over internal consistency
between all code belonging to a software layer.
Domain-driven design tackles solution complexity because it fo-
cuses on the areas of the system that are most subject to change—in
other words, the business domains. It places emphasis on capturing
the knowledge that is most likely to require experts outside of the field
of software.
THE SOFTWARE ORGANIZATION 227
The Model The Conversation And Yes The Code
Vehicle.java
Vehicle 1
G F -- u - e - e - a - l - r --- C -- a -- r ----------- F V P - T A .. - . u a o e - c - r c s c l - n o - i i e n - t ( c - i d l g o - e it - i n r y r - e - a - t c - e - t - i ( - o ) -- n - ) ----- Ho c v w a e r d h s i o c d l w e iff s e e i w r n e a g n n e tl t y n t e o fr r r o a t m l r ? eat pas F c s o o e n r n c c g e a e r r r n s s e w a d n e w d a i g f t r u u h e u n e y d l s H . e . . a e rs r y t e , a I t n t a h d lk i n w in k h g I a c a t a b th n o e u s t e ... 2 3 4 5 6 7 8 9 1 1 0 1 } i p n u t b e l p p p p p r i u u u u u c f b b b b b a l l l l l c i i i i i i e n c c c c c t C e F P v v d a a r o o o o c r s f i i u i i a d d b t n { c l i g e T A e o u c n r g c V g e n e e e ( g l t h t D F e e i V i a r c t e r c l a P l e i e o t o n c s e c g t ( i { i ( D i t t ) i o i y ; r o n ( e ) n ; ( c d ) t i ; i r o e n c t d i i o r n) e ; ction);
Refill(Amt) 12 public Gear getGear();
S ... hiftGear(Gear) 1 1 15 3 4 p p u u b b l l i i c c F v u o e i l d g R e e t f F i u l e l l (F () u ; el fuel);
Person 1 17 6 } public void ShiftGear(Gear gear);
... 1 19 8 interface Person
------------------------- 20{
E E n xi t t e (C r( a C r a ) r) 2 2 2 1 3 2 } v v o o i i d d E E n x t it e ( r C ( a C r a r c c a a r) r ; );
A team is participating in domain-driven design when they model,
communicate, and develop according to the core business-domain
logic of a solution and do so using a common domain language, known
as a ubiquitous language. Software specialists work intimately with
domain experts to capture the domain model, using domain terms,
and embed the domain terminology into their code.
The benefits are systems designed to flex and evolve in a way that
reflects how the business will change. Major changes will create major
system changes; minor business changes will require minor system
changes.
ORGANIZING AROUND DOMAINS
If we accept that structuring our system architecture according to
business domains is the preferred approach, then we can in turn start
thinking about structuring teams according to discrete domain ag-
gregates. A domain aggregate can be thought of as a set of domain
concepts that are very tightly interrelated with each other. It can be
a customer and their demographics or a shopping cart and all of the
independent order items in it. Domain aggregates are made up of do-
main entities and all of their invariants—in other words, dependent
domain objects that are retrieved together, updated together, and oth-
erwise change together. The Inverse Conway Maneuver is most effec-
tively applied when we think about partitioning software into separate
domain aggregates. This allows us to organize teams so that they can
be focused on the software required for a limited number of these
228 ORGANIZING TOWARD AGILITY
separate business domain aggregates.
In larger systems, DDD recommends that we place our domain
aggregates into separate bounded contexts. A bounded context places
a hard boundary around a domain aggregate, or possibly a small num-
ber of highly dependent domain aggregates. In a nutshell, we define
bounded contexts according to distinct but possibly related domains
of knowledge. A bounded context could be set up around a payments
domain aggregate, a customer, accounts and agreements, or charging
and billing. Bounded contexts can nest, with larger ones representing
entire systems and a smaller one representing a single domain service.
We may then refine our bounded contexts by grouping smaller
domain aggregates into larger composite domains and dividing larger
domains into separate but related component domains. We explore
how different domain aggregates relate to each other and what the de-
pendencies are between them. This allows us to suggest bounded con-
texts that can serve as the basis for a team structure that minimizes
the number and impact of dependencies that cross teams.
Structuring teams around bounded contexts is a good way to
achieve an acceptable level of independence when multiple teams are
working on a large-scale system. While we may want teams and eco-
systems to be truly independent, complete independence is often an
impossibility. In the real world, we often have to settle for decoupling
the dependencies across teams and ecosystems of teams. Defining
bounded contexts around decoupled domain aggregates allows us to
achieve this.
THE SOFTWARE ORGANIZATION 229
Customer Contract Team
Contracts
Product Plans Team
Account
Terms and Plans
Conditions Aggregate
Pricing
Customer
Aggregate
Discounts
Demographics
Contact Info
Products
Key: Domain Aggregate Services
Bounded Context
Cross Aggregate / Context Relationship
Defining bounded contexts for teams and the aggregates they work on
Ruth Nielsen, another product owner on the initiative, talked
about how reorganizing according to bounded contexts helped to turn
their program around:
We continued to advocate for owning how we wanted
to structure ourselves. We showed the impact of the
development-by-contract approach to our throughput.
Eventually we were given the reins back.
Right away the other product owners and I agreed
that we couldn’t focus on getting components done in
isolation; if we just built the button, or just the mes-
sage, and so on, we wouldn’t have a product. Instead
we structured our work so we could incrementally
show how user activity was translated to the Alberta
230 ORGANIZING TOWARD AGILITY
Information System and back again. This is what the
province cared about, and this is what our stakeholders
cared about. There was no point showing something to
the province if it wasn’t working end to end. So we or-
ganized around building end-to-end functionality. We
organized around user feedback.
We ended up forming teams around distinct but re-
lated domains, each within their own bounded context.
Each team was expected to work cross-functionally,
delivering an end-to-end slice of functionality that
demonstrated a complete journey from in-store POS
to the provincial disbursement information system and
back again.
Ruth, Stephanie, and the rest of the leads across the teams col-
laborated on how to go back to a cross-functional team structure like
they had before, but with a subtle yet distinct difference. Team mem-
bers would form into smaller feature cells around discrete bounded
contexts.
Ruth discussed how the approach kept things manageable:
Teams were tightly defined and people could work
within a small group, according to a tight set of features
within a particular bounded context. Team members
got to learn the entire stack without being overwhelmed
by the entirety of what the program was doing. This
made developing end-to-end flows a lot easier to do.
After a few weeks of setup time, the teams began to gel
and throughput started to increase to almost thirty sto-
ries a sprint!
Stephanie added:
Allowing teams to form around specific domain-based
contexts increased the understanding of the value the
team was providing, toward end-to-end value being
returned. There was no going back to a siloed way of
THE SOFTWARE ORGANIZATION 231
working. We gave the teams ownership of something
tangible, something to be proud of; we were successful
because their work had meaning.
REPRESENTING THE SOFTWARE
ARTIFACTS OF YOUR BUSINESS
An important aspect of a bounded context is that it represents a hard
boundary, one where all the aggregates within the boundary are part
of a common consistent context. They represent a common view that
is only considered “true” within the boundary. Different representa-
tions of the same concept are allowed, and even to be expected, across
bounded contexts. What this means is that the software used to rep-
resent these concepts will be consistent only within a boundary. Thus,
we need to be explicit about dependencies across bounded contexts,
as well as in the definition, translation, and integration required when
crossing bounded contexts. This is important when thinking not only
from a software perspective but also, more importantly, from the per-
spective of what these concepts mean to the development teams and
business experts that work within a particular bounded context.
232 ORGANIZING TOWARD AGILITY
Customer Team Sales Team
Customer Prospect
Account Relationship
Company
Purchases
Revenue Campaign
Discussion
Product
Notes
Pipe-Line
Stage
Key:
Domain Aggregate
Bounded Context
Two views of the same thing
Within a bounded context, we ask software and business experts
to examine each domain aggregate and agree on what services (or op-
erations) are being provided by the aggregate, what domain entities are
being managed, what orchestration happens, and how these domain
entities within each aggregate can be retrieved, created, and stored
into a domain repository. Concepts like what is considered a valid state
or various other rules, workflow, and conditions are also explored. The
idea is to create a programmatic API that is expressed purely in busi-
ness concepts and business terms, such that if a business expert can
see past the programmatic syntax, they could see a living expression
of their business.
The relationship, dependencies, and interactions among de-
pendencies between bounded contexts can be illustrated by using a
bounded context map. A bounded context map can show not only the
THE SOFTWARE ORGANIZATION 233
relationship between the system boundaries but also the interaction
model being used by the teams that own the interaction model.
Customer Orders
Service
Provider
Customer Ordered
Credentials Address Product
Ordering
Payment Account Customer
Methods Shipping
Destination
Order
Travelling Entry
Demographics
Order
Contact Sale
info Funnel
CRM Sale
Prospect
Enablement
Channel Product
Contact Offer
In the above diagram, where the CRM and customer contexts
overlap, we have what Eric Evans calls a shared kernel, whereby im-
pacts to elements in the kernel impact both teams and require inti-
mate collaboration and shared code ownership; daily integration is
common, and perhaps a single repo or pipeline is in use. In the case of
this example, the teams agree that they need to act as traveling team
workers and come together to work on demographics and contact info.
This approach is appropriate when two teams are both working on in-
terrelated domain concepts for the first time or when major changes to
both teams’ representation of these domain concepts are being made.
Workable solutions will require trial and error across both teams; in-
tense collaboration will be required. Shared kernels can also come
from accidental architecture, dependency magnets, and other forms of
tight coupling. Where possible, try to refactor your solution to mini-
mize this form of coupling.
Many bounded contexts will be separate but still have some form
of dependency with another bounded context. Expressed as arrows
234 ORGANIZING TOWARD AGILITY
connecting the boundaries, these dependencies in this case are more
decoupled than the shared-kernel variety, and changes to ordering
code may only require minimal changes to customer code, which is
already expressed as a well-formed, stable customer API. In this case,
the customer team can act as a service provider to the orders team. The
customer team can gather requirements from the orders team, prefer-
ably in the form of acceptance tests, implement the changes needed,
and review/demo the results with the orders team. Eric Evans calls this
a customer/supplier relationship.
Finally, we will have cases where a bounded context will require
no change to the API or underlying code in order to support the needs
of the team/context with the dependency. In this situation, the supply-
ing team is really responsible for acting as an enabler. In our current
example, the orders team is being enabled by the CRM team as they
work on the sales domain. The CRM team is responsible for providing
a well-tested API that is easy and obvious to use and for providing
great support to the orders team when they have issues or questions.
Eric Evans calls this integration approach the published language
method.
Personally speaking, the idea that context boundaries and bounded
context maps are an effective way to organize boundaries across mul-
tiple teams on a large program is something I have been working with
clients on for over fifteen years at the time of this writing. Demarcating
context boundaries based on distinct domains in a way that respects
Dunbar’s numbers gives us an approach that lets us decouple our orga-
nization into separate pieces that can free them to experience change
at different speeds from each other, while at the same time bringing
people together based on their ability to collaborate. Using context
boundaries to group teams, code, and other knowledge together was
my very first stab at trying to think of more organizing structure that
enabled rather than stifled agility.
IDENTIFYING DOMAIN AGGREGATES
AND CONTEXT BOUNDARIES
For the most part, aggregates and boundaries can be identified by
THE SOFTWARE ORGANIZATION 235
simply taking an inventory of the most important subject areas of
your business. Then, we can ask how coupled these concepts are from
a business perspective. Working closely with business subject mat-
ter experts, it is relatively easy to come up with such a list. General
concepts like customer, account, billing, and product come to mind,
but make sure to find topics that are specific to the business you are
writing software for. For instance, in the world of pharmacies you
would likely have domains around prescriptions, disbursements, pa-
tients, and medical providers. The point here is many technologies try
to build solutions around abstract models and then struggle to adapt
these to the specifics of a problem space. I recommend you model your
solution and organize your teams around concrete business concepts
that matter to your stakeholders who directly serve the market. Let ab-
stract concepts evolve as you apply domain concepts to multiple areas.
There are also some additional ways you can think about carving
out domain aggregates into separate bounded contexts; often there are
various approaches we can take to identify the subtleties in a domain
that justify partitioning a portion of the overall model into a separate
bounded context:
• Regulatory and compliance: The requirements imposed
on a solution can often be housed into their own bounded
context, even if those requirements span a number of
other, adjacent domains. For instance, requirements that
come from “know your customer”–related regulations are
often consistent across many banking products and lines
of business. The rules, structure, validations, and other
business logic related to complying to these regulations
could be served up by common microservice infrastruc-
ture and injected into various parts of the solution. A
know-your-customer team would be responsible for a
KyC API and for collaborating and supporting other
development teams.
• Transaction rates: When transactions occur at dramati-
cally different rates from each other in a system, chances
are you have identified a distinct domain boundary that
can be decoupled into separate contexts. Customers
236 ORGANIZING TOWARD AGILITY
and their accounts tend to be acquired, updated, or
retired a lot less frequently than customers purchasing
new products. For telecom or financial products, we see
transactional activities taking place much more fre-
quently than we see products being purchased. Inventory
replenishment happens at its own cadence, less often
than customer transactions but typically more frequently
than changes to products being offered. When we com-
pare how many times data will need to change over time
across a solution, it becomes clearer which domains
should be more tightly coupled and which areas can be
more loosely coupled.
• Market actors: The needs of various customer segments,
user personas, and so on that make up your market actors
may be different enough that you define distinct bounded
contexts based on these specific needs. For instance, in
the world of banking, the workflow and the applications
used to serve global small business customers can often
be quite different from the kinds of large-scale process-
ing applications used to serve large commercial business
customers. The flows can be quite distinct, the require-
ments for reversibility and auditability can vary, and so
on. Concierge clients may also have a different feature set,
risk profile, and so on than other customers, and thus be
managed as a separate bounded context.
• Domain life cycle state: Our view of a domain can be
quite different based on where a domain entity can be in
its life cycle. We care about very different things when we
are managing a lead versus managing the transaction of a
real customer. Having distinct bounded contexts for both
leads and customers can often make sense. Likewise, we
may care about different aspects of a product when man-
aging its assembly versus marketing the product on our
website to consumers. Again, separate bounded contexts
for each of these product perspectives can make sense.
THE SOFTWARE ORGANIZATION 237
LIMITING DOMAIN COMPLEXITY PER TEAM
A natural question to ask is how much domain complexity a team can
handle. Skelton and Pais discuss using domain complexity as a guide
to determine this number. In my experience, this is a function of both
complexity and change being made to the domain, so I would amend
their guidance to include both complexity and degree of change, to
determine the number of domains a team can work on at a time:
• One complex domain or one domain undergoing a high
degree of change
• Two to three simple domains, or one domain going
through two or three simple changes
• Avoid a single team owning more than one complicated
domain or having to make substantial changes to more
than one domain at a time.
Again, these are good rules of thumb, and context matters. The
point here is to make sure that we keep cognitive load on teams man-
ageable while at the same time encouraging the teams to grow their
skills and knowledge. Looking at the team’s flow of work may give you
warning signs that the team is overwhelmed, as will asking teams how
they feel about the amount of domain complexity that they own.
THE MODERN WORLD OF MICROSERVICES
As mentioned previously, the thinking behind structuring teams so
they can develop distinct and decoupled bounded contexts has had
an influence on the direction and adoption of new architectural par-
adigms like container-based provisioning, microservices, and No-Sql.
Using modern development and deployment technologies, we can
take each one of our bounded contexts and portray it as a cohesive
codebase that is represented through a well-formed API and deployed
independently from the rest of the system using container-based tech-
nology. We deploy a separate container for each bounded context,
and each container includes the business logic, data access code, and
238 ORGANIZING TOWARD AGILITY
even—thanks to No-Sql technologies—the database itself. Some orga-
nizations are even experimenting with deploying formatting “naked”
UI code, so that application consumers have the option to skin a refer-
ence domain–based UI and hook that into their larger front end. We
can then maximize decoupling across each bounded context through
event-based coordination, perhaps using the latest event-streaming
platforms.
This book is in no way a text on software architecture, and there
are others who have delved far deeper into how to apply modern soft-
ware approaches than I have. But I’ll admit to an unbridled passion for
the subject. And it is worth pointing out that microservices, contain-
erization, event streaming, and No-Sql have been inspired by concepts
such as domain aggregates and bounded contexts.
When we guide the use of these more modern delivery technol-
ogies with domain-driven design and the Inverse Conway Maneuver,
we end up with a system that is decoupled in a way that allows teams
to work independently and intelligently on a larger system. We avoid
the dangers of the monolith and the dependency magnet. We are
able to deliver and operate these distinct parts of our system accord-
ing to natural seams within the system, which Skelton and Pais call
“fracture planes.” Each fracture plane can be supported in a way that
matches their unique needs. Each fracture plane will have its own rate
of change, its performance requirements and usage load, its security
needs, or other risk factors. Teams can thus fit their approach to the
profile of the fracture plane they are supporting. We get the best of
both worlds, a well-reasoned architecture that provides teams with
the freedom they need to deliver based on their context. We get to
scale with agility.
THE SOFTWARE ORGANIZATION 239
Payments Service
Credit Check CC Billing
CC Billing
Credit Check Service
Service Event
Event
CC Accounts
Event
Event
Event
Credit Card Plans Credit Card
Event
CC Account
Service
Credit Card
Service
Event
CC Plans
Service
Context boundaries structure teams as well as the work they do
It is worth being wary of the fact that when many traditional or-
ganizations look at how they are approaching their deployment of
technologies like cloud and microservices, they do not appear to bring
much of this thinking along with it.
Many of those responsible for the adoption of these approaches for-
get that these technologies are there to enable better self-organization
and increase the autonomy of teams. They mandate usage according
to detailed standards, gate cloud access through specialist teams, and
otherwise use these technologies to exert unnecessary control on
teams. Worse, they do not consider the relationship between domain-
bounded contexts, microservice topology, and team structure. The
result is often a worse mess than the monolith they started with, a
fragmented architecture and organizational mess we call the distrib-
uted monolith. Those leading the adoption of new technology would
do well to remember that the successful adoption of these tools with-
out increasing team autonomy is really not much of a success at all.
240 ORGANIZING TOWARD AGILITY
WHEN WE NEED TO ORGANIZE AROUND
TECHNOLOGY INSTEAD
While I have emphasized the importance of taking a business do-
main–based approach to partitioning systems and defining differ-
ent bounded contexts, there are situations where bounded contexts
should be based on technology considerations. This is often necessary
when a solution relies on a number of packaged software and inte-
grating legacy systems. In these cases, teams are forced to work with
system representations of various domains, and these representations
will vary from system to system, hence the need to define bounded
contexts from a systems perspective. Delivery flow will be consider-
ably different across systems, with changes involving older technology
being rather slow because of more manual testing, onerous deploy-
ments, poor documentation, and aging codebases. Both package prod-
ucts and legacy systems often do not have good support for modern
engineering tools and practices like test-driven development and con-
tinuous integration and deployment.
Finally, the ecosystem of tools (IDEs, build tools, testing tools, etc.)
around such technology tends to behave and feel very different across
various proprietary packages and legacy systems.
All of these factors make a compelling case to structure teams
around systems rather than domain aggregates. Using this approach,
we define bounded contexts for each system, and perhaps for discrete
modules within these systems. We can use a bounded context map
to identify the way we want teams to collaborate where domain enti-
ties are represented in multiple systems and need to work on the in-
tegration required to ensure the overall solution works in a consistent
way. It is important to note that this approach can suffer when the
systems under change are being stood up for the first time or under-
going a very large amount of change. Dependencies across teams can
make delivery an incredibly complicated affair. In these cases, it may
be better to start with a single team made up of one or two specialists
from each system and have them lay out a common understanding of
how requirements will cascade across the various systems. Once this
common understanding is established, it then becomes much more
feasible to scale out toward system-based teams.
IN SUMMARY
• Scaling organizational agility in many cases means treat-
ing the organization and the software that supports it as a
single, integrated system.
• Conway’s Law, implying that the dysfunction of your
software will match the dysfunction of your organiza-
tional structure, has been ignored by many an enterprise,
resulting in monolithic and fragmented systems that have
frozen organizations’ ability to deliver value quickly.
• We can use the Inverse Conway Maneuver to deliberately
partition our software solution around the communica-
tion pathways we want our teams to have, in other words
deliberately aligning software architecture to organiza-
tional design.
• Domain-driven design asks us to design software solu-
tions that intimately reflect business domain concepts
and domain language, according to how domain experts
think and speak about the business domain.
• Partitioning systems into domain aggregates and
bounded contexts allows us to define parts of the system
that change together and that are naturally decoupled
from the remainder of the system, as opposed to parti-
tioning the system based on technology internals, which
results in system parts that are highly dependent on each
other.
• We can structure teams around each bounded context,
allowing multiple teams to work in a reasonably autono-
mous way on a single system.
• A modern software stack using microservices, container-
ization, No-Sql, event streaming, and so on enables teams
to increase their ability to work within a bounded context
while minimizing the impact to other teams working
within a separate bounded context.
• When working on legacy systems and package software
solutions, the diversity in technology may require us to
set up teams and their bounded contexts around these
systems instead of domain-based bounded contexts.
THE SOFTWARE ORGANIZATION 243