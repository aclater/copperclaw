package com.redhat.copperclaw.sse;

import io.smallrye.mutiny.Multi;
import io.smallrye.mutiny.operators.multi.processors.BroadcastProcessor;
import org.eclipse.microprofile.reactive.messaging.Incoming;
import jakarta.enterprise.context.ApplicationScoped;
import java.util.concurrent.LinkedBlockingDeque;
import org.jboss.logging.Logger;

@ApplicationScoped
public class SseBridgeService {

    private static final Logger LOG = Logger.getLogger(SseBridgeService.class);

    /**
     * In-memory buffer of recent events for new SSE connections (replay on connect).
     */
    private final LinkedBlockingDeque<String> recentEvents = new LinkedBlockingDeque<>(100);

    /**
     * Broadcast processor — all connected SSE clients receive each event.
     */
    private final BroadcastProcessor<String> broadcaster = BroadcastProcessor.create();

    @Incoming("cycle-state-in")
    public void onCycleState(String msg) {
        enqueueAndBroadcast(msg);
    }

    @Incoming("commander-log-in")
    public void onCommanderLog(String msg) {
        enqueueAndBroadcast(msg);
    }

    private void enqueueAndBroadcast(String msg) {
        if (recentEvents.size() >= 100) {
            recentEvents.pollFirst();
        }
        recentEvents.offerLast(msg);
        broadcaster.onNext(msg);
        LOG.debugf("SSE broadcast: %s", msg.length() > 100 ? msg.substring(0, 100) + "..." : msg);
    }

    /**
     * Returns a Multi stream of all future events (for SSE subscribers).
     */
    public Multi<String> stream() {
        return broadcaster;
    }

    /**
     * Returns recent buffered events for replay to newly connected clients.
     */
    public Iterable<String> recentEvents() {
        return recentEvents;
    }
}
