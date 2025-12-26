/*
 * Simulación LoRaWAN con Gateways Fijos (Tradicional) - Salinas
 * Con medición de latencia end-to-end Y COBERTURA DINÁMICA
 * VERSIÓN FINAL: Sin configuración de potencia variable (usa valor por defecto 14 dBm)
 */

#include "ns3/core-module.h"
#include "ns3/lorawan-module.h"
#include "ns3/mobility-module.h"
#include <fstream>
#include <sstream>
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include <map>
#include <vector>
#include <algorithm>
#include <cmath>
#include "ns3/netanim-module.h"

using namespace ns3;
using namespace lorawan;

NS_LOG_COMPONENT_DEFINE("SalinasTraditionalGW");

// Variables globales para medición de latencia
std::map<uint32_t, Time> g_packetSentTimes;
std::vector<double> g_latencies;

// ========== VARIABLES PARA COBERTURA DINÁMICA ==========
std::ofstream g_coberturaFile;
const double LORA_MAX_RANGE = 15000.0; // 15 km alcance máximo LoRa

double CalculateDistanceToGW(Vector pos1, Vector pos2)
{
    double dx = pos1.x - pos2.x;
    double dy = pos1.y - pos2.y;
    return std::sqrt(dx * dx + dy * dy);
}

// Callback cuando un end device ENVÍA un paquete
void
PacketSentCallback(Ptr<const Packet> packet)
{
    g_packetSentTimes[packet->GetUid()] = Simulator::Now();
    NS_LOG_DEBUG("Paquete " << packet->GetUid() << " enviado en t=" 
                 << Simulator::Now().GetSeconds() << "s");
}

// Variable global para contar paquetes recibidos
uint32_t g_packetsReceivedByServer = 0;

// Callback cuando el Network Server RECIBE un paquete
void
OnPacketReceptionCallback(Ptr<const Packet> packet)
{
    g_packetsReceivedByServer++;
    
    // Calcular latencia end-to-end
    uint32_t packetId = packet->GetUid();
    
    if (g_packetSentTimes.find(packetId) != g_packetSentTimes.end())
    {
        Time sentTime = g_packetSentTimes[packetId];
        Time receivedTime = Simulator::Now();
        Time latency = receivedTime - sentTime;
        
        double latencyMs = latency.GetMilliSeconds();
        g_latencies.push_back(latencyMs);
        
        NS_LOG_DEBUG("Latencia paquete " << packetId << ": " << latencyMs << " ms");
        
        g_packetSentTimes.erase(packetId);
    }
}

// ========== FUNCIONES DE LOGGING Y COBERTURA ==========
std::ofstream g_posFile;

void CalculateCoverage(NodeContainer boats, NodeContainer gateways, double simTime)
{
    double currentTime = Simulator::Now().GetSeconds();
    
    uint32_t totalBoats = boats.GetN();
    uint32_t boatsInRange = 0;
    double totalDistance = 0.0;
    double minDistance = LORA_MAX_RANGE;
    double maxDistance = 0.0;
    
    // Para cada embarcación, encontrar distancia al gateway más cercano
    for (uint32_t i = 0; i < totalBoats; ++i)
    {
        Ptr<MobilityModel> boatMob = boats.Get(i)->GetObject<MobilityModel>();
        if (!boatMob) continue;
        
        Vector boatPos = boatMob->GetPosition();
        double minDistToGW = LORA_MAX_RANGE * 2; // Inicializar con valor alto
        
        // Buscar gateway más cercano
        for (uint32_t j = 0; j < gateways.GetN(); ++j)
        {
            Ptr<MobilityModel> gwMob = gateways.Get(j)->GetObject<MobilityModel>();
            if (!gwMob) continue;
            
            Vector gwPos = gwMob->GetPosition();
            double dist = CalculateDistanceToGW(boatPos, gwPos);
            
            if (dist < minDistToGW)
            {
                minDistToGW = dist;
            }
        }
        
        // Acumular estadísticas
        totalDistance += minDistToGW;
        
        if (minDistToGW < minDistance)
            minDistance = minDistToGW;
        if (minDistToGW > maxDistance)
            maxDistance = minDistToGW;
        
        // Contar si está en rango
        if (minDistToGW <= LORA_MAX_RANGE)
        {
            boatsInRange++;
        }
    }
    
    // Calcular métricas de cobertura
    double coveragePercentage = (totalBoats > 0) ? (double)boatsInRange / totalBoats * 100.0 : 0.0;
    double avgDistance = (totalBoats > 0) ? totalDistance / totalBoats : 0.0;
    
    // Guardar en CSV
    g_coberturaFile << currentTime << "," 
                    << totalBoats << "," 
                    << boatsInRange << "," 
                    << coveragePercentage << ","
                    << avgDistance << ","
                    << minDistance << ","
                    << maxDistance << "\n";
    
    NS_LOG_DEBUG("Cobertura t=" << currentTime << "s: " << coveragePercentage 
                 << "% (" << boatsInRange << "/" << totalBoats << "), "
                 << "dist_prom=" << avgDistance << "m");
    
    // Programar siguiente cálculo
    if (currentTime < simTime - 1)
    {
        Simulator::Schedule(Seconds(5.0), &CalculateCoverage, boats, gateways, simTime);
    }
}

void LogPositions(NodeContainer boats, NodeContainer gateways, NodeContainer server, double simTime)
{
    double currentTime = Simulator::Now().GetSeconds();
    
    for (uint32_t i = 0; i < boats.GetN(); ++i)
    {
        Ptr<MobilityModel> mob = boats.Get(i)->GetObject<MobilityModel>();
        if (mob)
        {
            Vector pos = mob->GetPosition();
            g_posFile << currentTime << "," << i << "," 
                     << pos.x << "," << pos.y << ",boat\n";
        }
    }
    
    for (uint32_t i = 0; i < gateways.GetN(); ++i)
    {
        Ptr<MobilityModel> mob = gateways.Get(i)->GetObject<MobilityModel>();
        if (mob)
        {
            Vector pos = mob->GetPosition();
            uint32_t nodeId = boats.GetN() + i;
            g_posFile << currentTime << "," << nodeId << "," 
                     << pos.x << "," << pos.y << ",gateway\n";
        }
    }
    
    Ptr<MobilityModel> mobNS = server.Get(0)->GetObject<MobilityModel>();
    if (mobNS)
    {
        Vector pos = mobNS->GetPosition();
        uint32_t nodeId = boats.GetN() + gateways.GetN();
        g_posFile << currentTime << "," << nodeId << "," 
                 << pos.x << "," << pos.y << ",server\n";
    }
    
    if (currentTime < simTime - 1)
    {
        Simulator::Schedule(Seconds(5.0), &LogPositions, boats, gateways, server, simTime);
    }
}

int main(int argc, char* argv[])
{
    int nDevices = 50;
    int nFixedGateways = 3;  // 3 gateways fijos
    int spreadingFactor = 7;
    double simulationTime = 600;
    
    CommandLine cmd;
    cmd.AddValue("nDevices", "Número de embarcaciones", nDevices);
    cmd.AddValue("nGateways", "Número de gateways fijos", nFixedGateways);
    cmd.AddValue("sf", "Spreading Factor", spreadingFactor);
    cmd.AddValue("simTime", "Tiempo de simulación", simulationTime);
    cmd.Parse(argc, argv);

    // Inicializar logging
    g_posFile.open("posiciones_tradicional_3gw.csv");
    g_posFile << "time,node_id,x,y,type\n";
    
    // Inicializar archivo de cobertura dinámica
    g_coberturaFile.open("cobertura_tradicional_3gw.csv");
    g_coberturaFile << "time,total_boats,boats_in_range,coverage_percent,avg_distance,min_distance,max_distance\n";
    
    NS_LOG_INFO("=== Simulación LoRaWAN Gateways Fijos (Tradicional) - Salinas ===");
    NS_LOG_INFO("Embarcaciones: " << nDevices << ", Gateways fijos: " << nFixedGateways);
    NS_LOG_INFO("Spreading Factor: SF" << spreadingFactor);
    NS_LOG_INFO("Potencia de transmisión: 14 dBm (valor por defecto)");
    NS_LOG_INFO("Alcance máximo LoRa configurado: " << LORA_MAX_RANGE << " metros");
    
    NodeContainer endDevices;
    endDevices.Create(nDevices);
    NodeContainer fixedGateways;
    fixedGateways.Create(nFixedGateways);
    
    // Movilidad de embarcaciones (Random Walk en área de Salinas)
    MobilityHelper mobilityED;
    mobilityED.SetPositionAllocator("ns3::RandomRectanglePositionAllocator",
                                     "X", StringValue("ns3::UniformRandomVariable[Min=0|Max=25000]"),
                                     "Y", StringValue("ns3::UniformRandomVariable[Min=0|Max=15000]"));
    mobilityED.SetMobilityModel("ns3::RandomWalk2dMobilityModel",
                                 "Speed", StringValue("ns3::ConstantRandomVariable[Constant=5.0]"),
                                 "Bounds", RectangleValue(Rectangle(0, 25000, 0, 15000)));
    mobilityED.Install(endDevices);
    
    // Gateways fijos en ubicaciones ESPECÍFICAS
    MobilityHelper mobilityGW;
    mobilityGW.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    mobilityGW.Install(fixedGateways);
    
    // Asignar posiciones específicas a cada gateway
    Ptr<MobilityModel> mobGW0 = fixedGateways.Get(0)->GetObject<MobilityModel>();
    mobGW0->SetPosition(Vector(500, 500, 0));  // Puerto Santa Rosa
    
    Ptr<MobilityModel> mobGW1 = fixedGateways.Get(1)->GetObject<MobilityModel>();
    mobGW1->SetPosition(Vector(4200, 9500, 0));  // Punta Carnero
    
    Ptr<MobilityModel> mobGW2 = fixedGateways.Get(2)->GetObject<MobilityModel>();
    mobGW2->SetPosition(Vector(3500, 2500, 0));  // La Libertad
    
    NS_LOG_INFO("✓ Gateways fijos posicionados en ubicaciones específicas:");
    NS_LOG_INFO("  GW1: Puerto Santa Rosa (500, 500)");
    NS_LOG_INFO("  GW2: Punta Carnero (4200, 9500)");
    NS_LOG_INFO("  GW3: La Libertad (3500, 2500)");
    
    // Canal de propagación marítimo
    Ptr<LogDistancePropagationLossModel> loss = CreateObject<LogDistancePropagationLossModel>();
    loss->SetPathLossExponent(2.2);  // Exponente para propagación sobre agua
    loss->SetReference(1, 7.7);
    Ptr<PropagationDelayModel> delay = CreateObject<ConstantSpeedPropagationDelayModel>();
    Ptr<LoraChannel> channel = CreateObject<LoraChannel>(loss, delay);
    
    LoraPhyHelper phyHelper;
    phyHelper.SetDeviceType(LoraPhyHelper::ED);
    phyHelper.SetChannel(channel);
    
    LorawanMacHelper macHelper;
    macHelper.SetRegion(LorawanMacHelper::EU);
    
    LoraHelper helper;
    helper.EnablePacketTracking();
    
    macHelper.SetDeviceType(LorawanMacHelper::ED_A);
    helper.Install(phyHelper, macHelper, endDevices);

    // Configurar Spreading Factor en end devices
    for (NodeContainer::Iterator j = endDevices.Begin(); j != endDevices.End(); ++j)
    {
        Ptr<Node> node = *j;
        Ptr<LoraNetDevice> loraNetDevice = node->GetDevice(0)->GetObject<LoraNetDevice>();
        Ptr<ClassAEndDeviceLorawanMac> mac = loraNetDevice->GetMac()->GetObject<ClassAEndDeviceLorawanMac>();
        mac->SetDataRate(12 - spreadingFactor);
    }
    
    phyHelper.SetDeviceType(LoraPhyHelper::GW);
    macHelper.SetDeviceType(LorawanMacHelper::GW);
    helper.Install(phyHelper, macHelper, fixedGateways);    

    // ========== NETWORK SERVER CON P2P ==========
    
    NodeContainer networkServer;
    networkServer.Create(1);
    
    InternetStackHelper internet;
    internet.Install(networkServer);
    internet.Install(fixedGateways);
    
    PointToPointHelper p2p;
    p2p.SetDeviceAttribute("DataRate", StringValue("5Mbps"));
    p2p.SetChannelAttribute("Delay", StringValue("2ms"));
    
    Ptr<Node> nsNode = networkServer.Get(0);
    P2PGwRegistration_t gwRegistration;
    
    Ipv4AddressHelper address;
    address.SetBase("10.0.0.0", "255.255.255.0");
    
    for (uint32_t i = 0; i < fixedGateways.GetN(); i++)
    {
        Ptr<Node> gwNode = fixedGateways.Get(i);
        NodeContainer pair(gwNode, nsNode);
        NetDeviceContainer link = p2p.Install(pair);
        address.Assign(link);
        address.NewNetwork();
        
        Ptr<PointToPointNetDevice> p2pDevServer = link.Get(1)->GetObject<PointToPointNetDevice>();
        gwRegistration.push_back(std::make_pair(p2pDevServer, gwNode));
    }    
    
    NetworkServerHelper nsHelper;
    nsHelper.SetEndDevices(endDevices);
    nsHelper.SetGatewaysP2P(gwRegistration);
    nsHelper.Install(nsNode);
    
    // Conectar callback para recepción en Network Server
    Ptr<NetworkServer> ns = nsNode->GetApplication(0)->GetObject<NetworkServer>();
    if (ns)
    {
        ns->TraceConnectWithoutContext("ReceivedPacket", MakeCallback(&OnPacketReceptionCallback));
        NS_LOG_INFO("✓ Callback de recepción conectado en Network Server");
    }
    
    ForwarderHelper forHelper;
    ApplicationContainer forwarderApps = forHelper.Install(fixedGateways);
    
    for (uint32_t i = 0; i < fixedGateways.GetN(); i++)
    {
        Ptr<Node> gwNode = fixedGateways.Get(i);
        Ptr<Application> app = forwarderApps.Get(i);
        Ptr<Forwarder> forwarder = app->GetObject<Forwarder>();
        
        Ptr<LoraNetDevice> loraNetDevice = nullptr;
        for (uint32_t j = 0; j < gwNode->GetNDevices(); j++)
        {
            Ptr<NetDevice> dev = gwNode->GetDevice(j);
            loraNetDevice = dev->GetObject<LoraNetDevice>();
            if (loraNetDevice)
            {
                break;
            }
        }
        
        if (loraNetDevice && forwarder)
        {
            loraNetDevice->SetReceiveCallback(MakeCallback(&Forwarder::ReceiveFromLora, forwarder));
        }
    }
    
    NS_LOG_INFO("Forwarder instalado y callbacks configurados");
    NS_LOG_INFO("Network Server con P2P instalado correctamente");    
    
    PeriodicSenderHelper appHelper;
    appHelper.SetPeriod(Seconds(60));
    appHelper.Install(endDevices);
    
    // Conectar callback de envío en end devices
    for (uint32_t i = 0; i < endDevices.GetN(); i++)
    {
        Ptr<Node> node = endDevices.Get(i);
        Ptr<LoraNetDevice> loraNetDevice = node->GetDevice(0)->GetObject<LoraNetDevice>();
        Ptr<LorawanMac> mac = loraNetDevice->GetMac();
        Ptr<ClassAEndDeviceLorawanMac> edMac = mac->GetObject<ClassAEndDeviceLorawanMac>();
        
        if (edMac)
        {
            edMac->TraceConnectWithoutContext("SentNewPacket", MakeCallback(&PacketSentCallback));
        }
    }
    
    NS_LOG_INFO("✓ Callbacks de envío conectados en " << endDevices.GetN() << " embarcaciones");
    NS_LOG_INFO("Configuración completada");
    
    LoraPacketTracker& tracker = helper.GetPacketTracker();
    
    Simulator::Stop(Seconds(simulationTime));

    // NetAnim
    AnimationInterface anim("salinas-traditional-animation.xml");
    for (uint32_t i = 0; i < endDevices.GetN(); ++i)
    {
        std::ostringstream desc;
        desc << "Boat-" << i;
        anim.UpdateNodeDescription(endDevices.Get(i), desc.str());
        anim.UpdateNodeColor(endDevices.Get(i), 0, 0, 255);
        anim.UpdateNodeSize(i, 3.0, 3.0);
    }
    for (uint32_t i = 0; i < fixedGateways.GetN(); ++i)
    {
        uint32_t nodeId = endDevices.GetN() + i;
        std::ostringstream desc;
        desc << "GW-Fixed-" << i;
        anim.UpdateNodeDescription(fixedGateways.Get(i), desc.str());
        anim.UpdateNodeColor(fixedGateways.Get(i), 255, 0, 0);
        anim.UpdateNodeSize(nodeId, 6.0, 6.0);
    }
    uint32_t nsNodeId = endDevices.GetN() + fixedGateways.GetN();
    anim.UpdateNodeDescription(networkServer.Get(0), "Network-Server");
    anim.UpdateNodeColor(networkServer.Get(0), 0, 255, 0);
    anim.UpdateNodeSize(nsNodeId, 8.0, 8.0);
    anim.EnablePacketMetadata(true);
    
    // Iniciar logging de posiciones Y cálculo de cobertura
    Simulator::Schedule(Seconds(0.0), &LogPositions, endDevices, fixedGateways, networkServer, simulationTime);
    Simulator::Schedule(Seconds(0.0), &CalculateCoverage, endDevices, fixedGateways, simulationTime);
    
    NS_LOG_INFO("✓ Análisis de cobertura dinámica iniciado");
    
    Simulator::Run();
    
    NS_LOG_INFO("========== RESULTADOS ARQUITECTURA TRADICIONAL ==========");
    
    std::string sent = tracker.CountMacPacketsGlobally(Seconds(0), Seconds(simulationTime));
    NS_LOG_INFO("Estadísticas: " << sent);
    
    std::istringstream iss(sent);
    double packetsSent = 0;
    double packetsReceived = 0;
    iss >> packetsSent >> packetsReceived;
    
    double pdr = (packetsSent > 0) ? (packetsReceived / packetsSent) * 100.0 : 0.0;
    
    // Calcular estadísticas de latencia
    double avgLatency = 0.0;
    double minLatency = 0.0;
    double maxLatency = 0.0;
    double stdDevLatency = 0.0;
    
    if (!g_latencies.empty())
    {
        double sum = 0.0;
        for (double lat : g_latencies)
        {
            sum += lat;
        }
        avgLatency = sum / g_latencies.size();
        
        minLatency = *std::min_element(g_latencies.begin(), g_latencies.end());
        maxLatency = *std::max_element(g_latencies.begin(), g_latencies.end());
        
        double variance = 0.0;
        for (double lat : g_latencies)
        {
            variance += (lat - avgLatency) * (lat - avgLatency);
        }
        stdDevLatency = std::sqrt(variance / g_latencies.size());
    }
    
    NS_LOG_INFO("Paquetes enviados: " << packetsSent);
    NS_LOG_INFO("Paquetes recibidos: " << packetsReceived);
    NS_LOG_INFO("PDR: " << pdr << "%");
    NS_LOG_INFO("---------- LATENCIA END-TO-END ----------");
    NS_LOG_INFO("Latencia promedio: " << avgLatency << " ms");
    NS_LOG_INFO("Latencia mínima: " << minLatency << " ms");
    NS_LOG_INFO("Latencia máxima: " << maxLatency << " ms");
    NS_LOG_INFO("Desviación estándar: " << stdDevLatency << " ms");
    NS_LOG_INFO("Muestras de latencia: " << g_latencies.size());
    
    std::ofstream csvFile;
    csvFile.open("resultados_tradicional_3gw.csv", std::ios::app);
    if (csvFile.is_open())
    {
        csvFile.seekp(0, std::ios::end);
        if (csvFile.tellp() == 0)
        {
            csvFile << "Embarcaciones,GatewaysFijos,SF,TiempoSim,PaquetesEnviados,"
                       "PaquetesRecibidos,PDR,LatenciaPromedio,LatenciaMin,LatenciaMax,StdDev\n";
        }
        csvFile << nDevices << "," << nFixedGateways << "," << spreadingFactor << "," 
                << simulationTime << "," << packetsSent << "," << packetsReceived << "," 
                << pdr << "," << avgLatency << "," << minLatency << "," 
                << maxLatency << "," << stdDevLatency << "\n";
        csvFile.close();
        NS_LOG_INFO("✓ Resultados exportados a CSV");
    }
    
    Simulator::Destroy();
    g_posFile.close();
    g_coberturaFile.close();
    NS_LOG_INFO("✓ Archivos de visualización y cobertura generados");
    NS_LOG_INFO("✓ Archivo de cobertura: cobertura_tradicional_3gw.csv");
    
    NS_LOG_INFO("Simulación finalizada");
    return 0;
}
