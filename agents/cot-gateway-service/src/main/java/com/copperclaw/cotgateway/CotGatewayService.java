package com.copperclaw.cotgateway;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.eclipse.microprofile.reactive.messaging.Channel;
import org.eclipse.microprofile.reactive.messaging.Emitter;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.event.Observes;
import jakarta.inject.Inject;
import io.quarkus.runtime.StartupEvent;
import io.quarkus.runtime.ShutdownEvent;
import java.net.DatagramPacket;
import java.net.InetAddress;
import java.net.MulticastSocket;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;
import org.jboss.logging.Logger;
import org.w3c.dom.Document;
import javax.xml.parsers.DocumentBuilderFactory;
import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;

@ApplicationScoped
public class CotGatewayService {

    private static final Logger LOG = Logger.getLogger(CotGatewayService.class);

    @Inject
    ObjectMapper objectMapper;

    @ConfigProperty(name = "copperclaw.cot.multicast.group", defaultValue = "239.2.3.1")
    String multicastGroup;

    @ConfigProperty(name = "copperclaw.cot.multicast.port", defaultValue = "6969")
    int multicastPort;

    @ConfigProperty(name = "copperclaw.cot.simulation.enabled", defaultValue = "true")
    boolean simulationEnabled;

    @ConfigProperty(name = "copperclaw.cot.simulation.interval-seconds", defaultValue = "30")
    long simulationIntervalSeconds;

    @Channel("cot-out")
    Emitter<String> cotEmitter;

    private final AtomicBoolean running = new AtomicBoolean(false);
    private Thread listenerThread;
    private Thread simulationThread;

    void onStart(@Observes StartupEvent ev) {
        running.set(true);
        if (simulationEnabled) {
            startSimulation();
        } else {
            startMulticastListener();
        }
    }

    void onStop(@Observes ShutdownEvent ev) {
        running.set(false);
        if (listenerThread != null) listenerThread.interrupt();
        if (simulationThread != null) simulationThread.interrupt();
    }

    private void startMulticastListener() {
        listenerThread = Thread.ofVirtual().name("cot-multicast-listener").start(() -> {
            try (MulticastSocket socket = new MulticastSocket(multicastPort)) {
                InetAddress group = InetAddress.getByName(multicastGroup);
                socket.joinGroup(group);
                LOG.infof("COT-GATEWAY: Joined multicast group %s:%d", multicastGroup, multicastPort);
                byte[] buf = new byte[65536];
                while (running.get()) {
                    DatagramPacket packet = new DatagramPacket(buf, buf.length);
                    socket.receive(packet);
                    String xml = new String(packet.getData(), 0, packet.getLength(), StandardCharsets.UTF_8);
                    processCoTXml(xml);
                }
            } catch (Exception e) {
                if (running.get()) LOG.errorf(e, "COT-GATEWAY: Multicast listener error");
            }
        });
    }

    private void startSimulation() {
        simulationThread = Thread.ofVirtual().name("cot-simulator").start(() -> {
            LOG.infof("COT-GATEWAY: Simulation mode active. Emitting synthetic CoT every %d seconds.", simulationIntervalSeconds);
            String[] targets = {"TGT-ECHO-001", "TGT-GAMMA-001", "TGT-DELTA-001", "TGT-GAMMA-002", "TGT-ECHO-002"};
            String[] grids = {"VICTOR-5-KILO-229-447", "VICTOR-5-KILO-312-509", "VICTOR-5-LIMA-088-271",
                              "VICTOR-4-NOVEMBER-441-218", "VICTOR-5-KILO-198-331"};
            int idx = 0;
            while (running.get()) {
                try {
                    Thread.sleep(simulationIntervalSeconds * 1000L);
                    String simXml = buildSimulatedCoT(targets[idx % targets.length], grids[idx % grids.length]);
                    processCoTXml(simXml);
                    idx++;
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                } catch (Exception e) {
                    LOG.errorf(e, "COT-GATEWAY: Simulation error");
                }
            }
        });
    }

    private void processCoTXml(String xml) {
        try {
            DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
            dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
            Document doc = dbf.newDocumentBuilder().parse(
                new ByteArrayInputStream(xml.getBytes(StandardCharsets.UTF_8))
            );
            var root = doc.getDocumentElement();
            String uid = root.getAttribute("uid");
            String how = root.getAttribute("how");
            String time = root.getAttribute("time");
            String type = root.getAttribute("type");
            var pointNode = doc.getElementsByTagName("point").item(0);
            String lat = pointNode != null ? ((org.w3c.dom.Element) pointNode).getAttribute("lat") : "";
            String lon = pointNode != null ? ((org.w3c.dom.Element) pointNode).getAttribute("lon") : "";

            Map<String, Object> cotJson = Map.of(
                "event_id", UUID.randomUUID().toString(),
                "cot_uid", uid,
                "cot_type", type,
                "cot_how", how,
                "timestamp", time,
                "lat", lat,
                "lon", lon,
                "raw_xml", xml,
                "source", simulationEnabled ? "SIMULATION" : "MULTICAST"
            );
            String json = objectMapper.writeValueAsString(cotJson);
            cotEmitter.send(json);
            LOG.debugf("COT-GATEWAY: Published CoT event uid=%s type=%s", uid, type);
        } catch (Exception e) {
            LOG.errorf(e, "COT-GATEWAY: Failed to parse CoT XML");
        }
    }

    private String buildSimulatedCoT(String targetId, String grid) {
        String uid = "SIM-" + targetId + "-" + UUID.randomUUID().toString().substring(0, 8);
        return """
            <?xml version='1.0' encoding='UTF-8'?>
            <event version='2.0' uid='%s' type='a-f-G-I' how='m-g'
                   time='%s' start='%s' stale='%s'>
              <point lat='41.123' lon='44.456' hae='0' ce='50' le='50'/>
              <detail>
                <contact callsign='%s'/>
                <remarks>COPPERCLAW simulation event for %s at grid %s</remarks>
              </detail>
            </event>
            """.formatted(uid,
                java.time.Instant.now().toString(),
                java.time.Instant.now().toString(),
                java.time.Instant.now().plusSeconds(300).toString(),
                targetId, targetId, grid);
    }
}
