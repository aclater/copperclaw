package com.redhat.copperclaw.state;

import org.eclipse.microprofile.reactive.messaging.Channel;
import org.eclipse.microprofile.reactive.messaging.Emitter;
import org.eclipse.microprofile.reactive.messaging.Incoming;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import org.jboss.logging.Logger;

@ApplicationScoped
public class StateService {

    private static final Logger LOG = Logger.getLogger(StateService.class);

    @Inject
    CycleStateStore store;

    @Channel("cycle-state-publish")
    Emitter<String> cycleStateEmitter;

    @Incoming("isr-tasking-in")
    public void onIsrTasking(String msg) { updateState(msg, "ISR-TASKING"); }

    @Incoming("collection-in")
    public void onCollection(String msg) { updateState(msg, "COLLECTION"); }

    @Incoming("assessment-in")
    public void onAssessment(String msg) { updateState(msg, "ALL-SOURCE-ANALYST"); }

    @Incoming("nomination-in")
    public void onNomination(String msg) { updateState(msg, "TARGET-NOMINATION"); }

    @Incoming("authorization-in")
    public void onAuthorization(String msg) { updateState(msg, "COMMANDER"); }

    @Incoming("execution-in")
    public void onExecution(String msg) { updateState(msg, "EXECUTION"); }

    @Incoming("bda-in")
    public void onBda(String msg) { updateState(msg, "BDA"); }

    @Incoming("develop-in")
    public void onDevelop(String msg) { updateState(msg, "DEVELOP"); }

    @Incoming("legal-review-in")
    public void onLegalReview(String msg) { updateState(msg, "LEGAL-REVIEW"); }

    @Incoming("cot-events-in")
    public void onCotEvent(String msg) { updateState(msg, "COT-GATEWAY"); }

    private void updateState(String msg, String agent) {
        try {
            store.upsert(msg, agent);
            String currentState = store.getCurrentStateJson();
            cycleStateEmitter.send(currentState);
        } catch (Exception e) {
            LOG.errorf(e, "StateService: error updating state from %s", agent);
        }
    }
}
