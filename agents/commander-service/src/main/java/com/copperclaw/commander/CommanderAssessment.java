package com.copperclaw.commander;

/**
 * POJO representing the commander's assessment of a TNP.
 * Published to cycle-state when a TNP is received, before operator input.
 */
public class CommanderAssessment {
    public String tnpId;
    public String targetId;
    public String targetCodename;
    public String assessmentSummary;
    public boolean pidMet;
    public boolean rocChecklistClean;
    public String concernsIdentified;
    public String recommendedAction;
    public String timestamp;

    public CommanderAssessment() {}
}
