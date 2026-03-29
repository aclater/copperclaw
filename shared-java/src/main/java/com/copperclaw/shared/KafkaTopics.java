package com.copperclaw.shared;

public final class KafkaTopics {
    private KafkaTopics() {}
    public static final String ISR_TASKING       = "copperclaw.isr-tasking";
    public static final String COLLECTION        = "copperclaw.collection";
    public static final String ASSESSMENT        = "copperclaw.assessment";
    public static final String NOMINATION        = "copperclaw.nomination";
    public static final String AUTHORIZATION     = "copperclaw.authorization";
    public static final String EXECUTION         = "copperclaw.execution";
    public static final String BDA               = "copperclaw.bda";
    public static final String DEVELOP           = "copperclaw.develop";
    public static final String CYCLE_STATE       = "copperclaw.cycle-state";
    public static final String COMMANDER_LOG     = "copperclaw.commander-log";
    public static final String OPERATOR_COMMANDS = "copperclaw.operator-commands";
    public static final String LEGAL_REVIEW      = "copperclaw.legal-review";
    public static final String COT_IN            = "copperclaw.cot-in";
    public static final String COT_OUT           = "copperclaw.cot-out";
}
