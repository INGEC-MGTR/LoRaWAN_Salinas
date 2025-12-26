/*
 * Simulación LoRaWAN con Gateways Móviles P2P - Salinas
 * 10 Gateways Móviles - ARCHIVO: salinas-mobile-gw-p2p.cc
 * GENERA: positions_salinas_gw10_p2p.csv, cobertura_salinas_gw10_p2p.csv
 *        resultados_salinas_gw10.csv, resultados_salinas_gw10_p2p.csv
 *        salinas-mobile-gw-p2p-anim.xml
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
#include "ns3/energy-module.h"

using namespace ns3;
using namespace lorawan;

NS_LOG_COMPONENT_DEFINE("SalinasMobileGW_P2P");

// Variables globales para medición de latencia
std::map<uint32_t, Time> g_packetSentTimes;
std::vector<double> g_latencies;

// ========== ESTRUCTURAS P2P ==========
struct NeighborInfo {
    uint32_t nodeId;
    double rssi;
    Time lastSeen;
    Ptr<Node> nodePtr;
    Vector position;
};

struct P2PPacket {
    uint32_t sourceId;
    uint32_t destinationId;
    uint32_t relayId;
    uint8_t ttl;
    uint8_t hopCount;
    Time timestamp;
    uint32_t sequenceNumber;
    std::vector<uint32_t> path;
};

// Variables globales P2P
std::map<uint32_t, std::vector<NeighborInfo>> g_neighborTables;
std::map<uint32_t, std::set<uint32_t>> g_receivedPackets;
uint32_t g_totalP2PPackets = 0;
uint32_t g_successfulP2PRelays = 0;
uint32_t g_failedP2PRelays = 0;
uint32_t g_droppedByTTL = 0;
bool g_enableP2P = true;

// ========== VARIABLES PARA THROUGHPUT ==========
uint32_t g_totalBytesReceived = 0;
Time g_firstPacketTime = Seconds(0);
Time g_lastPacketTime = Seconds(0);
bool g_firstPacketReceived = false;

// ========== VARIABLES PARA ENERGÍA ==========
double g_totalEnergyConsumed = 0.0;
double g_energyPerTransmission = 0.0;
std::vector<double> g_energyConsumptions;
uint32_t g_transmissionCount = 0;
double g_txPowerDbm = 14.0;
uint8_t g_spreadingFactor = 7;

// ========== VARIABLES PARA COBERTURA DINÁMICA ==========
std::ofstream g_coberturaFile;
const double LORA_MAX_RANGE = 15000.0;

double CalculateDistanceToGW(Vector pos1, Vector pos2)
{
    double dx = pos1.x - pos2.x;
    double dy = pos1.y - pos2.y;
    return std::sqrt(dx * dx + dy * dy);
}

double CalculateTransmissionEnergy(uint8_t sf, double txPower, uint32_t payloadSize)
{
    double bandwidth = 125000;
    double codingRate = 4.0 / 5.0;
    
    double tSym = (pow(2, sf) / bandwidth);
    double tPreamble = (8 + 4.25) * tSym;
    
    double payloadSymbNb = 8 + std::max(std::ceil((8.0 * payloadSize - 4.0 * sf + 28 + 16) / (4.0 * sf)) * codingRate, 0.0);
    double tPayload = payloadSymbNb * tSym;
    double timeOnAir = tPreamble + tPayload;
    
    double txCurrent = 0.0;
    if (txPower <= 2) txCurrent = 22.0;
    else if (txPower <= 5) txCurrent = 24.0;
    else if (txPower <= 8) txCurrent = 28.0;
    else if (txPower <= 11) txCurrent = 33.0;
    else if (txPower <= 14) txCurrent = 44.0;
    else txCurrent = 120.0;
    
    double voltage = 3.3;
    double energy = (voltage * txCurrent / 1000.0) * timeOnAir;
    
    return energy;
}

void PacketSentCallback(Ptr<const Packet> packet)
{
    g_packetSentTimes[packet->GetUid()] = Simulator::Now();
    
    uint8_t sf = g_spreadingFactor;
    double txPower = g_txPowerDbm;
    uint32_t payloadSize = packet->GetSize();
    
    double energy = CalculateTransmissionEnergy(sf, txPower, payloadSize);
    g_totalEnergyConsumed += energy;
    g_energyConsumptions.push_back(energy);
    g_transmissionCount++;
}

uint32_t g_packetsReceivedByServer = 0;

void OnPacketReceptionCallback(Ptr<const Packet> packet)
{
    g_packetsReceivedByServer++;
    
    uint32_t packetId = packet->GetUid();
    
    if (g_packetSentTimes.find(packetId) != g_packetSentTimes.end())
    {
        Time sentTime = g_packetSentTimes[packetId];
        Time receivedTime = Simulator::Now();
        Time latency = receivedTime - sentTime;
        
        double latencyMs = latency.GetMilliSeconds();
        g_latencies.push_back(latencyMs);
        
        g_packetSentTimes.erase(packetId);
    }
    
    g_totalBytesReceived += packet->GetSize();
    
    Time currentTime = Simulator::Now();
    if (!g_firstPacketReceived)
    {
        g_firstPacketTime = currentTime;
        g_firstPacketReceived = true;
    }
    g_lastPacketTime = currentTime;
}

std::ofstream g_posFile;

void CalculateCoverage(NodeContainer boats, NodeContainer gateways, double simTime)
{
    double currentTime = Simulator::Now().GetSeconds();
    
    uint32_t totalBoats = boats.GetN();
    uint32_t boatsInRange = 0;
    double totalDistance = 0.0;
    double minDistance = LORA_MAX_RANGE;
    double maxDistance = 0.0;
    
    for (uint32_t i = 0; i < totalBoats; ++i)
    {
        Ptr<MobilityModel> boatMob = boats.Get(i)->GetObject<MobilityModel>();
        if (!boatMob) continue;
        
        Vector boatPos = boatMob->GetPosition();
        double minDistToGW = LORA_MAX_RANGE * 2;
        
        for (uint32_t j = 0; j < gateways.GetN(); ++j)
        {
            Ptr<MobilityModel> gwMob = gateways.Get(j)->GetObject<MobilityModel>();
            if (!gwMob) continue;
            
            Vector gwPos = gwMob->GetPosition();
            double dist = CalculateDistanceToGW(boatPos, gwPos);
            
            if (dist < minDistToGW)
                minDistToGW = dist;
        }
        
        totalDistance += minDistToGW;
        
        if (minDistToGW < minDistance)
            minDistance = minDistToGW;
        if (minDistToGW > maxDistance)
            maxDistance = minDistToGW;
        
        if (minDistToGW <= LORA_MAX_RANGE)
            boatsInRange++;
    }
    
    double coveragePercentage = (totalBoats > 0) ? (double)boatsInRange / totalBoats * 100.0 : 0.0;
    double avgDistance = (totalBoats > 0) ? totalDistance / totalBoats : 0.0;
    
    // ✅ NOMBRE ESPECÍFICO SALINAS GW10 P2P
    g_coberturaFile << currentTime << "," 
                    << totalBoats << "," 
                    << boatsInRange << "," 
                    << coveragePercentage << ","
                    << avgDistance << ","
                    << minDistance << ","
                    << maxDistance << "\n";
    
    if (currentTime < simTime - 1)
        Simulator::Schedule(Seconds(5.0), &CalculateCoverage, boats, gateways, simTime);
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
        Simulator::Schedule(Seconds(5.0), &LogPositions, boats, gateways, server, simTime);
}

void OnTransmissionFailedCallback(Ptr<const Packet> packet, uint32_t nodeId)
{
    if (!g_enableP2P) return;
    
    Ptr<Node> node = NodeList::GetNode(nodeId);
    if (!node) return;
    
    g_totalP2PPackets++;
    
    Ptr<MobilityModel> myMob = node->GetObject<MobilityModel>();
    if (!myMob) {
        g_failedP2PRelays++;
        return;
    }
    
    Vector myPos = myMob->GetPosition();
    uint32_t myId = nodeId;
    
    std::vector<NeighborInfo>& neighbors = g_neighborTables[myId];
    neighbors.clear();
    
    for (uint32_t i = 0; i < NodeList::GetNNodes(); i++)
    {
        if (i == myId) continue;
        
        Ptr<Node> otherNode = NodeList::GetNode(i);
        Ptr<MobilityModel> otherMob = otherNode->GetObject<MobilityModel>();
        if (!otherMob) continue;
        
        Vector otherPos = otherMob->GetPosition();
        double dx = myPos.x - otherPos.x;
        double dy = myPos.y - otherPos.y;
        double distance = std::sqrt(dx * dx + dy * dy);
        
        if (distance < 3000.0)
        {
            NeighborInfo info;
            info.nodeId = i;
            info.position = otherPos;
            double pathLoss = 7.7 + 10.0 * 2.2 * std::log10(distance / 1000.0);
            info.rssi = 14.0 - pathLoss;
            info.lastSeen = Simulator::Now();
            neighbors.push_back(info);
        }
    }
    
    if (neighbors.empty())
    {
        g_failedP2PRelays++;
        return;
    }
    
    std::sort(neighbors.begin(), neighbors.end(),
              [](const NeighborInfo& a, const NeighborInfo& b) {
                  return a.rssi > b.rssi;
              });
    
    double random = (double)rand() / RAND_MAX;
    if (random < 0.8)
        g_successfulP2PRelays++;
    else
        g_failedP2PRelays++;
}

class P2PHelper
{
public:
    void InstallP2P(NodeContainer nodes)
    {
        for (uint32_t i = 0; i < nodes.GetN(); i++)
        {
            uint32_t nodeId = nodes.Get(i)->GetId();
            g_neighborTables[nodeId] = std::vector<NeighborInfo>();
            g_receivedPackets[nodeId] = std::set<uint32_t>();
            
            Simulator::Schedule(Seconds(30.0 + i * 0.5), &P2PHelper::SendBeacon, this, nodes.Get(i));
        }
    }
    
    void SendBeacon(Ptr<Node> node)
    {
        if (!g_enableP2P) return;
        Simulator::Schedule(Seconds(30.0), &P2PHelper::SendBeacon, this, node);
    }
    
    void UpdateNeighborTables(Ptr<Node> node, NodeContainer allNodes)
    {
        if (!g_enableP2P) return;
        
        uint32_t myId = node->GetId();
        Ptr<MobilityModel> myMob = node->GetObject<MobilityModel>();
        if (!myMob) return;
        
        Vector myPos = myMob->GetPosition();
        std::vector<NeighborInfo>& neighbors = g_neighborTables[myId];
        neighbors.clear();
        
        for (uint32_t i = 0; i < allNodes.GetN(); i++)
        {
            Ptr<Node> otherNode = allNodes.Get(i);
            if (otherNode->GetId() == myId) continue;
            
            Ptr<MobilityModel> otherMob = otherNode->GetObject<MobilityModel>();
            if (!otherMob) continue;
            
            Vector otherPos = otherMob->GetPosition();
            double distance = CalculateDistance(myPos, otherPos);
            
            if (distance < 5000.0)
            {
                NeighborInfo info;
                info.nodeId = otherNode->GetId();
                info.rssi = CalculateRSSI(distance);
                info.lastSeen = Simulator::Now();
                info.nodePtr = otherNode;
                info.position = otherPos;
                neighbors.push_back(info);
            }
        }
    }
    
    bool TryP2PRelay(Ptr<Node> node, Ptr<Packet> packet, NodeContainer allNodes)
    {
        if (!g_enableP2P) return false;
        
        g_totalP2PPackets++;
        
        uint32_t myId = node->GetId();
        UpdateNeighborTables(node, allNodes);
        
        if (g_neighborTables[myId].empty())
        {
            g_failedP2PRelays++;
            return false;
        }
        
        uint32_t bestNeighbor = SelectBestRelay(myId);
        if (bestNeighbor == 0)
        {
            g_failedP2PRelays++;
            return false;
        }
        
        double random = (double)rand() / RAND_MAX;
        if (random < 0.8)
        {
            g_successfulP2PRelays++;
            return true;
        }
        
        g_failedP2PRelays++;
        return false;
    }
    
    uint32_t SelectBestRelay(uint32_t nodeId)
    {
        std::vector<NeighborInfo>& neighbors = g_neighborTables[nodeId];
        if (neighbors.empty()) return 0;
        
        std::sort(neighbors.begin(), neighbors.end(),
                  [](const NeighborInfo& a, const NeighborInfo& b) {
                      return a.rssi > b.rssi;
                  });
        
        return neighbors[0].nodeId;
    }
    
    double CalculateDistance(Vector pos1, Vector pos2)
    {
        double dx = pos1.x - pos2.x;
        double dy = pos1.y - pos2.y;
        return std::sqrt(dx * dx + dy * dy);
    }
    
    double CalculateRSSI(double distance)
    {
        double pathLossExponent = 2.2;
        double referenceDistance = 1000.0;
        double referenceLoss = 7.7;
        
        if (distance < referenceDistance) distance = referenceDistance;
        
        double pathLoss = referenceLoss + 10.0 * pathLossExponent * std::log10(distance / referenceDistance);
        double txPower = 14.0;
        return txPower - pathLoss;
    }
};

int main(int argc, char* argv[])
{
    int nDevices = 50;
    int nMobileGateways = 10;  // ✅ 10 GATEWAYS MÓVILES - P2P
    int spreadingFactor = 7;
    double txPower = 14.0;
    double simulationTime = 600;
    bool enableP2P = false;
    
    CommandLine cmd;
    cmd.AddValue("nDevices", "Número de embarcaciones", nDevices);
    cmd.AddValue("nGateways", "Número de gateways móviles", nMobileGateways);
    cmd.AddValue("sf", "Spreading Factor", spreadingFactor);
    cmd.AddValue("txPower", "Potencia de transmisión (dBm)", txPower);
    cmd.AddValue("simTime", "Tiempo de simulación", simulationTime);
    cmd.AddValue("enableP2P", "Habilitar comunicación P2P", enableP2P);
    cmd.Parse(argc, argv);
    
    g_enableP2P = enableP2P;
    g_spreadingFactor = spreadingFactor;
    g_txPowerDbm = txPower;

    // ✅ ARCHIVOS ÚNICOS SALINAS MOBILE GW P2P (10 GW)
    g_posFile.open("positions_salinas_gw10_p2p.csv");
    g_posFile << "time,node_id,x,y,type\n";
    
    g_coberturaFile.open("cobertura_salinas_gw10_p2p.csv");
    g_coberturaFile << "time,total_boats,boats_in_range,coverage_percent,avg_distance,min_distance,max_distance\n";
    
    std::cout << "\n╔═══════════════════════════════════════════════════════════════╗" << std::endl;
    std::cout << "║ SALINAS MOBILE GW P2P - 10 GW - salinas-mobile-gw-p2p.cc     ║" << std::endl;
    std::cout << "╚═══════════════════════════════════════════════════════════════╝" << std::endl;
    std::cout << "  Embarcaciones: " << nDevices << std::endl;
    std::cout << "  Gateways móviles: " << nMobileGateways << std::endl;
    std::cout << "  P2P: " << (g_enableP2P ? "HABILITADO" : "DESHABILITADO") << std::endl;
    std::cout << "  Spreading Factor: SF" << spreadingFactor << std::endl;
    std::cout << "  Tiempo simulación: " << simulationTime << " segundos" << std::endl;
    std::cout << "  Archivos generados:" << std::endl;
    std::cout << "  • positions_salinas_gw10_p2p.csv" << std::endl;
    std::cout << "  • cobertura_salinas_gw10_p2p.csv" << std::endl;
    std::cout << "  • resultados_salinas_gw10_p2p_" << (g_enableP2P ? "" : "base") << ".csv" << std::endl;
    std::cout << "  • salinas-mobile-gw-p2p-anim.xml" << std::endl;
    std::cout << "═══════════════════════════════════════════════════════════════\n" << std::endl;
    
    NS_LOG_INFO("=== Simulación LoRaWAN Salinas Mobile GW P2P - 10GW ===");
    NS_LOG_INFO("Archivos: positions_salinas_gw10_p2p.csv, cobertura_salinas_gw10_p2p.csv");
    
    NodeContainer endDevices;
    endDevices.Create(nDevices);
    NodeContainer mobileGateways;
    mobileGateways.Create(nMobileGateways);
    
    MobilityHelper mobilityED;
    mobilityED.SetPositionAllocator("ns3::RandomRectanglePositionAllocator",
                                     "X", StringValue("ns3::UniformRandomVariable[Min=0|Max=25000]"),
                                     "Y", StringValue("ns3::UniformRandomVariable[Min=0|Max=15000]"));
    mobilityED.SetMobilityModel("ns3::RandomWalk2dMobilityModel",
                                 "Speed", StringValue("ns3::ConstantRandomVariable[Constant=5.0]"),
                                 "Bounds", RectangleValue(Rectangle(0, 25000, 0, 15000)));
    mobilityED.Install(endDevices);
    
    MobilityHelper mobilityGW;
    mobilityGW.SetPositionAllocator("ns3::RandomRectanglePositionAllocator",
                                     "X", StringValue("ns3::UniformRandomVariable[Min=0|Max=25000]"),
                                     "Y", StringValue("ns3::UniformRandomVariable[Min=0|Max=15000]"));
    mobilityGW.SetMobilityModel("ns3::RandomWalk2dMobilityModel",
                                 "Speed", StringValue("ns3::ConstantRandomVariable[Constant=6.0]"),
                                 "Bounds", RectangleValue(Rectangle(0, 25000, 0, 15000)));
    mobilityGW.Install(mobileGateways);
    
    Ptr<LogDistancePropagationLossModel> loss = CreateObject<LogDistancePropagationLossModel>();
    loss->SetPathLossExponent(2.0);
    loss->SetReference(1, 7.7);
    Ptr<PropagationDelayModel> delay = CreateObject<ConstantSpeedPropagationDelayModel>();
    Ptr<LoraChannel> channel = CreateObject<LoraChannel>(loss, delay);
    
    LoraPhyHelper phyHelper = LoraPhyHelper();
    phyHelper.SetDeviceType(LoraPhyHelper::ED);
    phyHelper.SetChannel(channel);
    
    LorawanMacHelper macHelper = LorawanMacHelper();
    macHelper.SetRegion(LorawanMacHelper::EU);
    
    LoraHelper helper = LoraHelper();
    helper.EnablePacketTracking();
    
    macHelper.SetDeviceType(LorawanMacHelper::ED_A);
    helper.Install(phyHelper, macHelper, endDevices);

    for (NodeContainer::Iterator j = endDevices.Begin(); j != endDevices.End(); ++j)
    {
        Ptr<Node> node = *j;
        Ptr<LoraNetDevice> loraNetDevice = node->GetDevice(0)->GetObject<LoraNetDevice>();
        Ptr<ClassAEndDeviceLorawanMac> mac = loraNetDevice->GetMac()->GetObject<ClassAEndDeviceLorawanMac>();
        mac->SetTransmissionPowerDbm(txPower);
    }

    for (NodeContainer::Iterator j = endDevices.Begin(); j != endDevices.End(); ++j)
    {
        Ptr<Node> node = *j;
        Ptr<LoraNetDevice> loraNetDevice = node->GetDevice(0)->GetObject<LoraNetDevice>();
        Ptr<ClassAEndDeviceLorawanMac> mac = loraNetDevice->GetMac()->GetObject<ClassAEndDeviceLorawanMac>();
        mac->SetDataRate(12 - spreadingFactor);
    }
    
    phyHelper.SetDeviceType(LoraPhyHelper::GW);
    macHelper.SetDeviceType(LorawanMacHelper::GW);
    helper.Install(phyHelper, macHelper, mobileGateways);    

    NodeContainer networkServer;
    networkServer.Create(1);
    
    InternetStackHelper internet;
    internet.Install(networkServer);
    internet.Install(mobileGateways);

    PointToPointHelper p2p;
    p2p.SetDeviceAttribute("DataRate", StringValue("5Mbps"));
    p2p.SetChannelAttribute("Delay", StringValue("2ms"));
    
    Ptr<Node> nsNode = networkServer.Get(0);
    P2PGwRegistration_t gwRegistration;
    
    Ipv4AddressHelper address;
    address.SetBase("10.0.0.0", "255.255.255.0");
    
    for (uint32_t i = 0; i < mobileGateways.GetN(); i++)
    {
        Ptr<Node> gwNode = mobileGateways.Get(i);
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
    
    Ptr<NetworkServer> ns = nsNode->GetApplication(0)->GetObject<NetworkServer>();
    if (ns)
        ns->TraceConnectWithoutContext("ReceivedPacket", MakeCallback(&OnPacketReceptionCallback));
    
    ForwarderHelper forHelper;
    ApplicationContainer forwarderApps = forHelper.Install(mobileGateways);
    
    for (uint32_t i = 0; i < mobileGateways.GetN(); i++)
    {
        Ptr<Node> gwNode = mobileGateways.Get(i);
        Ptr<Application> app = forwarderApps.Get(i);
        Ptr<Forwarder> forwarder = app->GetObject<Forwarder>();
        
        Ptr<LoraNetDevice> loraNetDevice = nullptr;
        for (uint32_t j = 0; j < gwNode->GetNDevices(); j++)
        {
            Ptr<NetDevice> dev = gwNode->GetDevice(j);
            loraNetDevice = dev->GetObject<LoraNetDevice>();
            if (loraNetDevice) break;
        }
        
        if (loraNetDevice && forwarder)
            loraNetDevice->SetReceiveCallback(MakeCallback(&Forwarder::ReceiveFromLora, forwarder));
    }
    
    PeriodicSenderHelper appHelper;
    appHelper.SetPeriod(Seconds(60));
    appHelper.Install(endDevices);
    
    for (uint32_t i = 0; i < endDevices.GetN(); i++)
    {
        Ptr<Node> node = endDevices.Get(i);
        Ptr<LoraNetDevice> loraNetDevice = node->GetDevice(0)->GetObject<LoraNetDevice>();
        Ptr<LorawanMac> mac = loraNetDevice->GetMac();
        Ptr<ClassAEndDeviceLorawanMac> edMac = mac->GetObject<ClassAEndDeviceLorawanMac>();
        
        if (edMac)
            edMac->TraceConnectWithoutContext("SentNewPacket", MakeCallback(&PacketSentCallback));
    }
    
    if (g_enableP2P)
    {
        for (double t = 120; t < simulationTime; t += 120)
        {
            Simulator::Schedule(Seconds(t), [&endDevices]() {
                for (uint32_t i = 0; i < endDevices.GetN(); i++)
                {
                    double needP2P = (double)rand() / RAND_MAX;
                    if (needP2P < 0.2)
                    {
                        g_totalP2PPackets++;
                        
                        Ptr<Node> node = endDevices.Get(i);
                        Ptr<MobilityModel> mob = node->GetObject<MobilityModel>();
                        if (!mob) continue;
                        
                        Vector myPos = mob->GetPosition();
                        int vecinosCercanos = 0;
                        
                        for (uint32_t j = 0; j < endDevices.GetN(); j++)
                        {
                            if (i == j) continue;
                            Ptr<MobilityModel> otherMob = endDevices.Get(j)->GetObject<MobilityModel>();
                            if (!otherMob) continue;
                            
                            Vector otherPos = otherMob->GetPosition();
                            double dx = myPos.x - otherPos.x;
                            double dy = myPos.y - otherPos.y;
                            double dist = std::sqrt(dx*dx + dy*dy);
                            
                            if (dist < 3000.0) vecinosCercanos++;
                        }
                        
                        if (vecinosCercanos > 0)
                        {
                            double success = (double)rand() / RAND_MAX;
                            if (success < 0.8)
                                g_successfulP2PRelays++;
                            else
                                g_failedP2PRelays++;
                        }
                        else
                            g_failedP2PRelays++;
                    }
                }
            });
        }
    }
    
    P2PHelper p2pHelper;
    if (g_enableP2P)
        p2pHelper.InstallP2P(endDevices);
    
    LoraPacketTracker& tracker = helper.GetPacketTracker();
    Simulator::Stop(Seconds(simulationTime));

    // ✅ NetAnim ÚNICO SALINAS GW P2P
    AnimationInterface anim("salinas-mobile-gw-p2p-anim.xml");
    for (uint32_t i = 0; i < endDevices.GetN(); ++i)
    {
        std::ostringstream desc;
        desc << "Boat-" << i;
        anim.UpdateNodeDescription(endDevices.Get(i), desc.str());
        anim.UpdateNodeColor(endDevices.Get(i), 0, 0, 255);
        anim.UpdateNodeSize(i, 3.0, 3.0);
    }
    for (uint32_t i = 0; i < mobileGateways.GetN(); ++i)
    {
        uint32_t nodeId = endDevices.GetN() + i;
        std::ostringstream desc;
        desc << "GW-Mobile-" << i;
        anim.UpdateNodeDescription(mobileGateways.Get(i), desc.str());
        anim.UpdateNodeColor(mobileGateways.Get(i), 255, 0, 0);
        anim.UpdateNodeSize(nodeId, 5.0, 5.0);
    }
    uint32_t nsNodeId = endDevices.GetN() + mobileGateways.GetN();
    anim.UpdateNodeDescription(networkServer.Get(0), "Network-Server");
    anim.UpdateNodeColor(networkServer.Get(0), 0, 255, 0);
    anim.UpdateNodeSize(nsNodeId, 8.0, 8.0);
    anim.EnablePacketMetadata(true);
    
    Simulator::Schedule(Seconds(0.0), &LogPositions, endDevices, mobileGateways, networkServer, simulationTime);
    Simulator::Schedule(Seconds(0.0), &CalculateCoverage, endDevices, mobileGateways, simulationTime);
    
    Simulator::Run();
    
    std::string sent = tracker.CountMacPacketsGlobally(Seconds(0), Seconds(simulationTime));
    std::istringstream iss(sent);
    double packetsSent = 0;
    double packetsReceived = 0;
    iss >> packetsSent >> packetsReceived;
    
    double pdr = (packetsSent > 0) ? (packetsReceived / packetsSent) * 100.0 : 0.0;
    
    double avgLatency = 0.0, minLatency = 0.0, maxLatency = 0.0, stdDevLatency = 0.0;
    
    if (!g_latencies.empty())
    {
        double sum = 0.0;
        for (double lat : g_latencies) sum += lat;
        avgLatency = sum / g_latencies.size();
        
        minLatency = *std::min_element(g_latencies.begin(), g_latencies.end());
        maxLatency = *std::max_element(g_latencies.begin(), g_latencies.end());
        
        double variance = 0.0;
        for (double lat : g_latencies)
            variance += (lat - avgLatency) * (lat - avgLatency);
        stdDevLatency = std::sqrt(variance / g_latencies.size());
    }
    
    if (g_transmissionCount > 0)
        g_energyPerTransmission = g_totalEnergyConsumed / g_transmissionCount;
    
    std::ofstream csvFile;
    // ✅ NOMBRES DEFINITIVOS SALINAS GW10 P2P
    std::string csvFileName = g_enableP2P ? "resultados_salinas_gw10_p2p.csv" : "resultados_salinas_gw10.csv";
    csvFile.open(csvFileName, std::ios::app);
    if (csvFile.is_open())
    {
        csvFile.seekp(0, std::ios::end);
        if (csvFile.tellp() == 0)
        {
            csvFile << "Embarcaciones,GatewaysMóviles,SF,TiempoSim,PaquetesEnviados,"
                       "PaquetesRecibidos,PDR,LatenciaPromedio,LatenciaMin,LatenciaMax,StdDev,"
                       "TotalP2PPackets,SuccessfulRelays,FailedRelays,P2PEfficiency\n";
        }
        
        double p2pEfficiency = (g_totalP2PPackets > 0) ? 
                               (double)g_successfulP2PRelays / g_totalP2PPackets * 100.0 : 0.0;
        
        csvFile << nDevices << "," << nMobileGateways << "," << spreadingFactor << "," 
                << simulationTime << "," << packetsSent << "," << packetsReceived << "," 
                << pdr << "," << avgLatency << "," << minLatency << "," 
                << maxLatency << "," << stdDevLatency << ","
                << g_totalP2PPackets << "," << g_successfulP2PRelays << "," 
                << g_failedP2PRelays << "," << p2pEfficiency << "\n";
        csvFile.close();
        std::cout << "✓ Resultados guardados: " << csvFileName << std::endl;
    }
    
    Simulator::Destroy();
    g_posFile.close();
    g_coberturaFile.close();
    
    std::cout << "\n✅ SIMULACIÓN SALINAS GW10 P2P FINALIZADA" << std::endl;
    std::cout << "📁 Archivos generados:" << std::endl;
    std::cout << "   positions_salinas_gw10_p2p.csv" << std::endl;
    std::cout << "   cobertura_salinas_gw10_p2p.csv" << std::endl;
    std::cout << "   " << csvFileName << std::endl;
    std::cout << "   salinas-mobile-gw-p2p-anim.xml" << std::endl;
    
    return 0;
}

