# Meeting notes

# summary-0626

**Meeting summary**

## **Quick recap**

This meeting was an onboarding session for a collaborative project between the Chai Lab team and the Pritzker School of Molecular Engineering (PME) team to integrate AI with robotic battery research. The team discussed connecting their Neurico AI system with the Battery Lab robotic platform, which can autonomously assemble and test coin cells using three robotic arms and a liquid dispenser. Nathan explained that the current system requires human-specified inputs for electrolyte compositions and cell configurations, while the outputs include electrochemical performance data like EIS spectra and Nyquist plots. The group agreed that the first step would be to develop a connector or template to process robot outputs and generate specific human instructions, with Shane and Davi working on the technical implementation while Nathan provides documentation about the robot's capabilities and requirements. The team also discussed improving the data quality for NeuralCode by providing zinc battery-specific datasets rather than water activity data, and establishing a closed-loop system where AI generates hypotheses, the robot runs experiments, and the results feed back into the AI system for continuous improvement.

## **Next steps**

### **Haokun**

* Re-invite Nathan to the private repo if access issues persist.

### **Nathan**

* Send initial documentation about the robot system (inputs, outputs, examples of human instructions) to the team by today.  
* Share the GitHub repo of Battery Lab with the team.

### **Shane**

* Send a calendar invite for the weekly Friday meeting. (not really)

### **Collaboration**

* Shane and Davi: Develop a prototype connector/template for NeuriCo to interface with the robot, based on the documentation provided by Nathan.  
* Shane and Davi: Investigate how to build a connection layer for NeuroGo to access the robot's output data stored on the cluster.  
* Zhiyuan and Nathan: Arrange a lab visit for Shane and Davi to see the robot in action, tentatively scheduled for next Monday.  
* All: Keep frequent discussions and updates on the Discord channel, ensuring activity at least every two days.

## **Summary**

### **AI Battery Research Team Onboarding**

The meeting was an onboarding session for new team members working on AI for battery research. Zhiyuan introduced himself as a postdoc in PME focusing on AI for batteries, while Davi mentioned he was joining from a physics background to work on AI research. Shane, a computer science undergraduate, expressed some nervousness about the pressure but confirmed his role as a main laboratory assistant. The team discussed sharing a private document with previous research proposals, though there appeared to be access issues that needed to be resolved.

### **Neural-AI Battery Research Integration**

The team introduced themselves and discussed a project to connect neural code with robotic systems for battery research at the Pritzker School of Molecular Engineering. Nathan explained that the Battery Lab robotic platform currently requires human-specified inputs for electrolyte compositions and cell configurations, and produces outputs like electrical-chemical performance data. The team outlined their goal to integrate a neural AI system into the existing robotic setup, with Shane and Davi tasked to help develop the necessary connections and prototype templates.

### **Battery System Robot Integration Plan**

Nathan explained the battery system robot process involving physically assembling KOMI cells and testing them for electrochemical performance. Shane suggested using high-quality data, including human-labeled information about material concentrations and combinations, to improve AI decision-making. The team agreed that the first goal is to connect the robot system with their AI, with W and Shane tasked to develop a connector or template to process robot outputs and generate specific human instructions.

### **Robot Prototype Project Planning**

The team discussed plans for a robot prototype project where Nathan will provide documentation and GitHub access to help with development. They agreed to schedule a lab visit for next Monday to see the robot demonstration, with Zhiyuan offering to show the robot's capabilities. The project scope was clarified by Davi as aiming to create a closed loop system where NeuralCo generates hypotheses, the robot runs tests, and NeuralCo analyzes results to refine hypotheses, though human intervention may also be needed.

### **Feedback Mechanisms System Discussion**

The team discussed feedback mechanisms for their system, with Zhiyuan noting that previously they could only input datasets and questions without providing feedback. They identified two key issues with the current workflow: using datasets from carbon dioxide reduction rather than zinc batteries, which may affect proposal quality, and the need for human feedback insertion. Nathan was asked to provide more details about previous discussions regarding workflow improvements, though the conversation ended before he could fully respond.

### **Zinc Battery Data Pipeline Improvements**

The team discussed improving the data pipeline for zinc battery analysis to ensure it doesn't proceed with fake data when essential datasets are missing. Shane emphasized the need for the resource finder to identify missing data requirements and alert human users, rather than using toy datasets. When Nathan asked about using computational chemistry techniques like DFT or molecular dynamics for cases with insufficient data, Zhiyuan confirmed this approach could be considered but noted it's not the current priority, suggesting instead focusing on combining robotic and neural golfers with potential future integration of simulation methods.

### **Nuroko Workflow Development Planning**

The team discussed developing a new workflow specifically for Nuroko rather than trying to integrate with an existing system. Zhiyuan clarified that their preferred output is not an article but feasible feedback for their robot to conduct experiments, with electrochemical performance data to be provided later. The team agreed to maintain frequent communication on Discord, with a maximum of two days between updates, and established a weekly Friday meeting for reflection and alignment. Nathan will compile documentation about the robot's capabilities, inputs, and outputs, including examples of human interactions with the robot, for review before the next meeting.

# BatteryLab Info

**BatteryLab Info**

To follow up on our discussion about connecting NeuriCo to our robotic platform. Below is an overview of how BatteryLab works, what it takes as input and produces as output, where our data currently stands, and what I'd propose as next steps. I've kept the hardware details brief and pointed to specific parts of the repo: [https://github.com/AmanchukwuLab/BatteryLab/tree/main](https://github.com/AmanchukwuLab/BatteryLab/tree/main).

**(1) What is BatteryLab**

It's a semi-autonomous workstation for assembling and testing CR2032 coin cells, built to accelerate electrolyte discovery. It uses two Meca500 robotic arms (assembly \+ crimping/storage), a Dobot MG400 with a Sartorius rLine dispenser for liquid handling, a linear rail, and a crimper (which we are still building but we're manually crimping them right now). It's based on Dr. Helge Stein's AutoBASS system ([https://github.com/Helge-Stein-Group/AutoBASS](https://github.com/Helge-Stein-Group/AutoBASS)).

The high-level hardware description is in the repo README under "Hardware Requirements" and the three "Robot" subsections: [https://github.com/AmanchukwuLab/BatteryLab/blob/main/README.md](https://github.com/AmanchukwuLab/BatteryLab/blob/main/README.md)

The key conceptual point for integration is that today the robot executes human-specified recipes- it picks materials from fixed predetermined positions and runs a fixed assembly protocol. There is no decision-making layer choosing what to test. That decision layer is exactly what NeuriCo provides.

**(2) Input interface**

The cleanest integration seam is the electrolyte planner module, which already defines a machine-readable recipe format. See the README at: BatteryLab/electrolyte\_planner/README.md. The robot consumes a JSON recipe file. Each cell is one entry:

\[  
  {  
    "recipe\_name": "baseline\_cell\_01",  
    "target\_electrolyte": {  
      "name": "baseline\_target",  
      "volume": 0.05,  
      "v": {"water": 0.5, "propylene glycol": 0.5}  
    }  
  }  
\]

Field meanings:  
\- "v" \= volume fractions of solvents (must sum to 1\)  
\- "s" \= salt molarities (optional field)  
\- "a" \= additive molarities (optional field)  
\- "volume" \= total electrolyte volume to dispense  
\- "recipe\_name" \= identifier that stays linked to the assembled cell's record

This is the target format for NeuriCo's output. When NeuriCo proposes a candidate electrolyte, it needs to emit a dict in this shape. For reference, our recent NeuriCo run (detailed in Haokun's repo: [https://github.com/Hypognic-AI/water-activity-eutectics-83ad/tree/main](https://github.com/Hypogenic-AI/water-activity-eutectics-83ad/tree/main)) produced 30 ranked candidates already expressed as (solvent, water mole fraction, salt). Those map onto this schema almost directly, with a mole-fraction → volume-fraction conversion being the main translation step. The planner also handles feasibility checking against current vial inventory, tip contamination tracking, and low/empty vial flags. So if NeuriCo requests something the current stock can't make, the planner will catch it. Inventory state persists to JSON across restarts.

**(3) The output interface**

After a cell is assembled, it's linked to its recipe (name \+ full JSON payload). Electrochemical testing is then run on a potentiostat. The two measurements relevant to our scope:

\- Ionic conductivity — short (\~2 hr) test, symmetric stainless/separator/stainless cell, no anode or cathode. Primary near-term metric.  
\- Coulombic efficiency — multi-day Zn||Cu cycling. Secondary metric.

The raw output from the potentiostat is instrument files (EIS spectra / Nyquist data and cycle-by-cycle voltage-current traces), not clean scalars. We'll try to own a parsing/interpretation layer that converts these into structured values NeuriCo can reason over, e.g. bulk resistance → ionic conductivity, and CE-by-cycle. My plan is to hardcode a reasonable equivalent circuit for our zinc system and auto-fit with impedance.py, then hand NeuriCo a clean dict rather than raw curves. (Task on our side: confirming the exact equivalent circuit — I'm working on that.)

**(4) Past data**

During the meeting Shane asked whether we have prior runs of the robot making electrolytes with human good/bad labels on the results. Short answer is not yet. Previous work on our system focused on mechanical calibration and machine-vision correction rather than generating cycling datasets, so there are no robot-produced electrolyte and test-result pairs to hand over right now.

The one dataset we do have is the lab's water-activity dataset (\~594 measurements across many solvent/salt combinations), which is what the recent NeuriCo run trained its GP surrogate on. However, it contains no zinc-containing salts, so the zinc predictions are extrapolations from literature correlations rather than measured data. Generating the first real zinc electrolyte \+ measurement pairs is what we hope the robot loop will produce, and it directly addresses the biggest gap in the current model.

**(5) The research loop pipeline**

Proposed flow:  
1\. NeuriCo proposes candidate electrolyte(s) → emits recipe JSON  
2\. Recipe lands in a shared folder (rsync poll, as discussed)  
3\. Robot assembles the cells from the recipe file  
4\. Human runs the electrochemical test (the robot can't do this step yet)  
5\. Potentiostat output → my parsing layer → structured results  
6\. Results sync back to NeuriCo → GP retrains → new proposal

The async gap in steps 2–5 (physical experiments take hours to days, vs. NeuriCo's default fast-computation assumption) is the main infrastructure piece to solve together, so NeuriCo's 3600s default timeout will also need adjusting for real experiment timescales.

**(6) Proposed next steps**

On NeuriCo's side:  
\- Build the data sync mechanism (rsync to shared folder) and the candidate-selector that maps NeuriCo output to recipe JSON (see section 2), so we can connect the NeuriCo system to BatteryLab system  
\- The async wait and resume handling (see Section 5\) so a run can pause for a physical experiment

On BatteryLab/Amanchukwu Lab's side:  
\- Manually collecting a first small batch of zinc water-activity data to seed the loop  
\- The battery domain template content in terms of what features matter, what counts as a good result  
\- The EIS/CE parsing layer (convert raw potentiostat files to structured scalars)

To discuss:  
\- The exact interface format for electrochemical performance results coming back (plain text vs. JSON dict \- what does NeuriCo prefer to ingest?)  
\- A concrete first milestone. Possibly, let's take the top \~5–10 candidates from the existing NeuriCo run, have the robot assemble them, measure ionic conductivity, and feed results back to retrain.  
