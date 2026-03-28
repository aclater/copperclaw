# OPERATOR LLM — TF KESTREL EQUIPMENT FLAVOR CONTEXT
# Injected into the operator system prompt as a read-only context block.
# Descriptive only — not operational instructions or schema defaults.
# Agents never see this text.

OPERATOR_EQUIPMENT_CONTEXT = """
TF KESTREL EQUIPMENT CONTEXT (FOR SITUATIONAL AWARENESS ONLY):

TF KESTREL's persistent ISR capability is built around two MC-12W Liberty 
aircraft operating under the callsigns RAVEN-1 and RAVEN-2. RAVEN-1 carries 
a combined synthetic aperture radar and electro-optical/infrared sensor suite 
with 18-hour endurance; it is currently committed to PIR-001 (VARNAK pattern 
of life) over VICTOR-5-KILO. RAVEN-2 is held in reserve and available for 
retasking. Signals intelligence support is provided by RC-135V/W Rivet Joint 
under the callsign EAGLE SIGINT, with intermittent coverage due to theatre-
level tasking competition. Ground-based SIGINT is available from SHADOW COMMS 
(KESTREL Signals Regiment) on a 48-hour response cycle. HUMINT source KITE-7 
has established access to the PRENN logistics network and is the primary source 
for Component DELTA intelligence; last report was 36 hours ago.

Attack aviation is provided by AH-64E Apache. Artillery support is M109A7 
Paladin for US-flagged fires and AS-90 for UK elements, coordinated through 
J3 FIRES. The attached KSOF element operates MH-60M DAP (Direct Action 
Penetrator) for HVI capture and direct action missions; KSOF is not available 
for routine tasks and requires COMKJTF coordination.

The adversary air defence threat is 9K38 Igla (SA-18 Grouse) MANPADS, assessed 
across all three SLV components and most likely concentrated with Component 
GAMMA. This threat requires mandatory assessment before any rotary-wing fires 
mission in VICTOR-5 or VICTOR-6 grid zones. Component GAMMA's indirect fire 
capability at STONEPILE is the Soviet-legacy 120mm 2B11 Sani mortar system. 
Component DELTA's electronic warfare disruption uses RP-377 series jamming 
equipment affecting Coalition UHF tactical communications.

These are contextual references to help you answer operator questions about 
available assets accurately. All agent outputs and schema fields use generic 
operational categories (e.g. PRECISION_STRIKE, SOF_DIRECT_ACTION). The 
frontend display map translates these to human-readable labels for the 
briefing console. Never instruct agents to use real platform designations 
in their outputs.
"""
