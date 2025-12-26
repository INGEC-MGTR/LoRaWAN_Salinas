/*
 * Simulación LoRaWAN con Gateways Móviles - Salinas
 * Con medición de latencia end-to-end
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

NS_LOG_COMPONENT_DEFINE("SalinasMobileGW");

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
double g_totalEnergyConsumed = 0.0;           // Energía total consumida (Joules)
double g_energyPerTransmission = 0.0;         // Energía promedio por transmisión
std::vector<double> g_energyConsumptions;     // Vector de consumos individuales
uint32_t g_transmissionCount = 0;             // Contador de transmisiones
double g_txPowerDbm = 14.0;                   // Potencia de transmisión configurada (dBm)
uint8_t g_spreadingFactor = 7;                // Spreading Factor configurado

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
// ========== FUNCIÓN PARA CALCULAR ENERGÍA ==========
/**
 * Calcula la energía consumida en una transmisión LoRa
 * Basado en el modelo de consumo del SX1276
 */
double CalculateTransmissionEnergy(uint8_t sf, double txPower, uint32_t payloadSize)
{
    // Parámetros del transceiver SX1276
    double bandwidth = 125000; // 125 kHz
    double codingRate = 4.0 / 5.0; // CR 4/5
    
    // Tiempo en el aire (Time on Air) en segundos
    double tSym = (pow(2, sf) / bandwidth); // Duración de un símbolo
    double tPreamble = (8 + 4.25) * tSym;   // Preámbulo
    
    double payloadSymbNb = 8 + std::max(std::ceil((8.0 * payloadSize - 4.0 * sf + 28 + 16) / (4.0 * sf)) * codingRate, 0.0);
    double tPayload = payloadSymbNb * tSym;
    double timeOnAir = tPreamble + tPayload;
    
    // Consumo de corriente según potencia de transmisión (mA)
    // Valores del datasheet SX1276
    double txCurrent = 0.0;
    if (txPower <= 2) txCurrent = 22.0;
    else if (txPower <= 5) txCurrent = 24.0;
    else if (txPower <= 8) txCurrent = 28.0;
    else if (txPower <= 11) txCurrent = 33.0;
    else if (txPower <= 14) txCurrent = 44.0;
    else txCurrent = 120.0; // 20 dBm
    
    // Voltaje de operación (V)
    double voltage = 3.3;
    
    // Energía = Potencia × Tiempo = (V × I) × t
    double energy = (voltage * txCurrent / 1000.0) * timeOnAir; // Joules
    
    return energy;
}

void
PacketSentCallback(Ptr<const Packet> packet)
{
    g_packetSentTimes[packet->GetUid()] = Simulator::Now();
    NS_LOG_DEBUG("Paquete " << packet->GetUid() << " enviado en t=" 
                 << Simulator::Now().GetSeconds() << "s");
    
    // Calcular energía consumida en esta transmisión
    // Asumimos SF7 y 14 dBm por defecto (estos valores se deberían obtener dinámicamente)
    uint8_t sf = g_spreadingFactor;  // Usa el SF configurado
    double txPower = g_txPowerDbm;  // Usa la potencia configurada
    uint32_t payloadSize = packet->GetSize();
    
    double energy = CalculateTransmissionEnergy(sf, txPower, payloadSize);
    g_totalEnergyConsumed += energy;
    g_energyConsumptions.push_back(energy);
    g_transmissionCount++;
    
    NS_LOG_DEBUG("Energía consumida: " << energy * 1000 << " mJ");
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
    
    // Registrar bytes y tiempos para throughput
    g_totalBytesReceived += packet->GetSize();
    
    Time currentTime = Simulator::Now();
    if (!g_firstPacketReceived)
    {
        g_firstPacketTime = currentTime;
        g_firstPacketReceived = true;
    }
    g_lastPacketTime = currentTime;
}

// ========== FUNCIONES DE LOGGING ==========
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
    
    // Guardar en CSV - NOMBRE ESPECÍFICO SALINAS 3GW
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

// Callback para transmisión fallida
void OnTransmissionFailedCallback(Ptr<const Packet> packet, uint32_t nodeId)
{
    if (!g_enableP2P) return;
    
    NS_LOG_DEBUG("Transmisión fallida del nodo " << nodeId << ", intentando P2P relay");
    
    // Buscar el nodo
    Ptr<Node> node = NodeList::GetNode(nodeId);
    if (!node) return;
    
    // Intentar relay P2P
    g_totalP2PPackets++;
    
    // Buscar vecinos
    Ptr<MobilityModel> myMob = node->GetObject<MobilityModel>();
    if (!myMob) {
        g_failedP2PRelays++;
        return;
    }
    
    Vector myPos = myMob->GetPosition();
    uint32_t myId = nodeId;
    
    // Actualizar tabla de vecinos
    std::vector<NeighborInfo>& neighbors = g_neighborTables[myId];
    neighbors.clear();
    
    // Buscar vecinos cercanos
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
        
        if (distance < 3000.0)  // 3 km de rango P2P
        {
            NeighborInfo info;
            info.nodeId = i;
            info.position = otherPos;
            // Calcular RSSI simple
            double pathLoss = 7.7 + 10.0 * 2.2 * std::log10(distance / 1000.0);
            info.rssi = 14.0 - pathLoss;
            info.lastSeen = Simulator::Now();
            neighbors.push_back(info);
        }
    }
    
    if (neighbors.empty())
    {
        g_failedP2PRelays++;
        NS_LOG_DEBUG("  No hay vecinos disponibles para relay");
        return;
    }
    
    // Ordenar por mejor RSSI
    std::sort(neighbors.begin(), neighbors.end(),
              [](const NeighborInfo& a, const NeighborInfo& b) {
                  return a.rssi > b.rssi;
              });
    
    // Simular relay exitoso con probabilidad 80%
    double random = (double)rand() / RAND_MAX;
    if (random < 0.8)
    {
        g_successfulP2PRelays++;
        NS_LOG_DEBUG("  ✓ P2P Relay exitoso hacia nodo " << neighbors[0].nodeId);
    }
    else
    {
        g_failedP2PRelays++;
        NS_LOG_DEBUG("  ✗ P2P Relay falló");
    }
}

// ========== CLASE P2P HELPER ==========
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
        NS_LOG_INFO("P2P instalado en " << nodes.GetN() << " nodos");
    }
    
    void SendBeacon(Ptr<Node> node)
    {
        if (!g_enableP2P) return;
        
        uint32_t nodeId = node->GetId();
        Ptr<MobilityModel> mob = node->GetObject<MobilityModel>();
        if (!mob) return;
        
        Vector myPos = mob->GetPosition();
        
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
    int nMobileGateways = 3;  // ✅ 3 GATEWAYS MÓVILES - SALINAS
    int spreadingFactor = 7;
    double txPower = 14.0;
    double simulationTime = 3600;  // 1 hora
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

    // ✅ ARCHIVOS CON NOMBRES ÚNICOS PARA SALINAS 3GW
    g_posFile.open("positions_salinas_movil_3gw.csv");
    g_posFile << "time,node_id,x,y,type\n";
    
    g_coberturaFile.open("cobertura_salinas_movil_3gw.csv");
    g_coberturaFile << "time,total_boats,boats_in_range,coverage_percent,avg_distance,min_distance,max_distance\n";
    
    std::cout << "\n╔════════════════════════════════════════════════════════╗" << std::endl;
    std::cout << "║  SALINAS MÓVIL 3GW - ARCHIVO: salinas-mobile-3gw.cc   ║" << std::endl;
    std::cout << "╚════════════════════════════════════════════════════════╝" << std::endl;
    std::cout << "  Embarcaciones: " << nDevices << std::endl;
    std::cout << "  Gateways móviles: " << nMobileGateways << std::endl;
    std::cout << "  P2P: " << (g_enableP2P ? "HABILITADO" : "DESHABILITADO") << std::endl;
    std::cout << "  Spreading Factor: SF" << spreadingFactor << std::endl;
    std::cout << "  Tiempo simulación: " << simulationTime << " segundos" << std::endl;
    std::cout << "  Archivos generados:" << std::endl;
    std::cout << "  • positions_salinas_movil_3gw.csv" << std::endl;
    std::cout << "  • cobertura_salinas_movil_3gw.csv" << std::endl;
    std::cout << "  • resultados_salinas_movil_3gw_" << (g_enableP2P ? "p2p" : "base") << ".csv" << std::endl;
    std::cout << "  • salinas-mobile-3gw-anim.xml" << std::endl;
    std::cout << "════════════════════════════════════════════════════════\n" << std::endl;
    
    NS_LOG_INFO("=== Simulación LoRaWAN Gateways Móviles - Salinas 3GW ===");
    NS_LOG_INFO("Archivos: positions_salinas_movil_3gw.csv, cobertura_salinas_movil_3gw.csv");
    NS_LOG_INFO("P2P: " << (g_enableP2P ? "HABILITADO" : "DESHABILITADO"));
    NS_LOG_INFO("Embarcaciones: " << nDevices << ", Gateways móviles: " << nMobileGateways);
    NS_LOG_INFO("Alcance máximo LoRa configurado: " << LORA_MAX_RANGE << " metros");
    
    NodeContainer endDevices;
    endDevices.Create(nDevices);
    NodeContainer mobileGateways;
    mobileGateways.Create(nMobileGateways);
    
    // ========== MOVILIDAD EMBARCACIONES (Random Walk 2D) ==========
    MobilityHelper mobilityED;
    mobilityED.SetPositionAllocator("ns3::RandomRectanglePositionAllocator",
                                     "X", StringValue("ns3::UniformRandomVariable[Min=0|Max=25000]"),
                                     "Y", StringValue("ns3::UniformRandomVariable[Min=0|Max=15000]"));
    mobilityED.SetMobilityModel("ns3::RandomWalk2dMobilityModel",
                                 "Speed", StringValue("ns3::UniformRandomVariable[Min=4.1|Max=6.2]"), // 8-12 nudos
                                 "Bounds", RectangleValue(Rectangle(0, 25000, 0, 15000)),
                                 "Distance", DoubleValue(2000.0));
    mobilityED.Install(endDevices);
    
    // ========== POSICIONES INICIALES ESTRATÉGICAS - 3 GATEWAYS MÓVILES ==========
    // Basadas en rutas pesqueras reales de Salinas
    MobilityHelper mobilityGW;
    Ptr<ListPositionAllocator> gwInitialPositions = CreateObject<ListPositionAllocator>();
    
    // Gateway Móvil 1: Ruta Norte hacia Punta Carnero (bearing 015°)
    gwInitialPositions->Add(Vector(5000, 5000, 15));
    
    // Gateway Móvil 2: Ruta Oeste hacia aguas profundas (bearing 270°)
    gwInitialPositions->Add(Vector(12000, 7500, 15));
    
    // Gateway Móvil 3: Ruta Suroeste zona pesca industrial (bearing 225°)
    gwInitialPositions->Add(Vector(10000, 11000, 15));
    
    mobilityGW.SetPositionAllocator(gwInitialPositions);
    mobilityGW.SetMobilityModel("ns3::RandomWalk2dMobilityModel",
                                 "Speed", StringValue("ns3::UniformRandomVariable[Min=5.1|Max=7.7]"), // 10-15 nudos
                                 "Bounds", RectangleValue(Rectangle(0, 25000, 0, 15000)),
                                 "Distance", DoubleValue(3000.0));
    mobilityGW.Install(mobileGateways);
    
    std::cout << "✓ Gateways móviles configurados (Salinas 3GW):" << std::endl;
    std::cout << "  GW-Móvil 1 (Ruta Norte): Inicio (5.0 km, 5.0 km)" << std::endl;
    std::cout << "  GW-Móvil 2 (Ruta Oeste): Inicio (12.0 km, 7.5 km)" << std::endl;
    std::cout << "  GW-Móvil 3 (Ruta Suroeste): Inicio (10.0 km, 11.0 km)" << std::endl;
    std::cout << "  Velocidad: 10-15 nudos (5.1-7.7 m/s)" << std::endl;
    std::cout << "  Patrón: Random Walk 2D (faenas de pesca)\n" << std::endl;
    
    Ptr<LogDistancePropagationLossModel> loss = CreateObject<LogDistancePropagationLossModel>();
    loss->SetPathLossExponent(2.0);
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

    // Configurar potencia de transmisión en todos los end devices
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

    // ========== NETWORK SERVER CON P2P ==========
    
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
    
    // Conectar callback para recepción en Network Server
    Ptr<NetworkServer> ns = nsNode->GetApplication(0)->GetObject<NetworkServer>();
    if (ns)
    {
        ns->TraceConnectWithoutContext("ReceivedPacket", MakeCallback(&OnPacketReceptionCallback));
        NS_LOG_INFO("✓ Callback de recepción conectado en Network Server");
    }
    
    ForwarderHelper forHelper;
    ApplicationContainer forwarderApps = forHelper.Install(mobileGateways);
    
    for (uint32_t i = 0; i < mobileGateways.GetN(); i++)
    {
        Ptr<Node> gwNode = mobileGateways.Get(i);
        Ptr<Application> app = forwarderApps.Get(i);
        Ptr<Forwarder> forwarder = app->GetObject<Forwarder>();
        
        NS_LOG_INFO("Gateway " << i << " tiene " << gwNode->GetNDevices() << " dispositivos:");
        
        Ptr<LoraNetDevice> loraNetDevice = nullptr;
        for (uint32_t j = 0; j < gwNode->GetNDevices(); j++)
        {
            Ptr<NetDevice> dev = gwNode->GetDevice(j);
            loraNetDevice = dev->GetObject<LoraNetDevice>();
            if (loraNetDevice)
            {
                NS_LOG_INFO("  - Dispositivo " << j << ": LoraNetDevice encontrado");
                break;
            }
        }
        
        if (loraNetDevice && forwarder)
        {
            loraNetDevice->SetReceiveCallback(MakeCallback(&Forwarder::ReceiveFromLora, forwarder));
            NS_LOG_INFO("✓ Callback ReceiveFromLora conectado para Gateway " << i);
        }
    }
    
    NS_LOG_INFO("Forwarder instalado y callbacks configurados");
    NS_LOG_INFO("Spreading Factor configurado: SF" << spreadingFactor);
    NS_LOG_INFO("Potencia de transmisión configurada: " << txPower << " dBm");
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
    
    // ========== SIMULACIÓN PERIÓDICA DE INTENTOS P2P ==========
    if (g_enableP2P)
    {
        // Cada 120 segundos, simular intentos de P2P en zonas con baja cobertura
        for (double t = 120; t < simulationTime; t += 120)
        {
            Simulator::Schedule(Seconds(t), [&endDevices]() {
                // Simular que algunos nodos intentan P2P
                for (uint32_t i = 0; i < endDevices.GetN(); i++)
                {
                    // 20% de probabilidad de necesitar P2P en cada check
                    double needP2P = (double)rand() / RAND_MAX;
                    if (needP2P < 0.2)  // 20% de los nodos
                    {
                        uint32_t nodeId = endDevices.Get(i)->GetId();
                        Ptr<Node> node = endDevices.Get(i);
                        Ptr<MobilityModel> mob = node->GetObject<MobilityModel>();
                        if (!mob) continue;
                        
                        g_totalP2PPackets++;
                        
                        // Buscar vecinos
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
                            // 80% éxito si hay vecinos
                            double success = (double)rand() / RAND_MAX;
                            if (success < 0.8)
                                g_successfulP2PRelays++;
                            else
                                g_failedP2PRelays++;
                        }
                        else
                        {
                            g_failedP2PRelays++;
                        }
                    }
                }
            });
        }
        NS_LOG_INFO("✓ Monitoreo P2P periódico programado");
    }
    
    // ========== INSTALAR SISTEMA P2P ==========
    P2PHelper p2pHelper;
    if (g_enableP2P)
    {
        NS_LOG_INFO("Instalando sistema P2P...");
        p2pHelper.InstallP2P(endDevices);
        NS_LOG_INFO("✓ Sistema P2P instalado");
    }
    else
    {
        NS_LOG_INFO("Sistema P2P deshabilitado");
    }
    NS_LOG_INFO("Configuración completada");
    
    LoraPacketTracker& tracker = helper.GetPacketTracker();
    
    Simulator::Stop(Seconds(simulationTime));

    // ✅ NetAnim - NOMBRE ESPECÍFICO SALINAS 3GW
    AnimationInterface anim("salinas-mobile-3gw-anim.xml");
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
    
    // Iniciar logging de posiciones Y cálculo de cobertura
    Simulator::Schedule(Seconds(0.0), &LogPositions, endDevices, mobileGateways, networkServer, simulationTime);
    Simulator::Schedule(Seconds(0.0), &CalculateCoverage, endDevices, mobileGateways, simulationTime);
    
    NS_LOG_INFO("✓ Análisis de cobertura dinámica iniciado - cobertura_salinas_movil_3gw.csv");
    
    Simulator::Run();
    
    NS_LOG_INFO("========== RESULTADOS SALINAS MÓVIL 3GW ==========");
    
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
    
    // ========== ESTADÍSTICAS P2P ==========
    if (g_enableP2P)
    {
        NS_LOG_INFO("---------- ESTADÍSTICAS P2P ----------");
        NS_LOG_INFO("Total intentos P2P: " << g_totalP2PPackets);
        NS_LOG_INFO("Relays exitosos: " << g_successfulP2PRelays);
        NS_LOG_INFO("Relays fallidos: " << g_failedP2PRelays);
        NS_LOG_INFO("Descartados por TTL: " << g_droppedByTTL);
        double p2pSuccessRate = (g_totalP2PPackets > 0) ? (double)g_successfulP2PRelays / g_totalP2PPackets * 100.0 : 0.0;
        NS_LOG_INFO("Tasa de éxito P2P: " << p2pSuccessRate << "%");
    }
    // ========== ESTADÍSTICAS DE THROUGHPUT ==========
    NS_LOG_INFO("---------- THROUGHPUT EFECTIVO ----------");
    
    if (g_firstPacketReceived && g_lastPacketTime > g_firstPacketTime)
    {
        double simulationDuration = (g_lastPacketTime - g_firstPacketTime).GetSeconds();
        
        // Throughput en bits por segundo
        double throughputBps = (g_totalBytesReceived * 8.0) / simulationDuration;
        double throughputKbps = throughputBps / 1000.0;
        
        // Throughput en paquetes por segundo
        double throughputPps = packetsReceived / simulationDuration;
        
        NS_LOG_INFO("Bytes totales recibidos: " << g_totalBytesReceived << " bytes");
        NS_LOG_INFO("Duración efectiva: " << simulationDuration << " segundos");
        NS_LOG_INFO("Throughput: " << throughputBps << " bps");
        NS_LOG_INFO("Throughput: " << throughputKbps << " Kbps");
        NS_LOG_INFO("Throughput: " << throughputPps << " paquetes/segundo");
    }
    else
    {
        NS_LOG_INFO("No hay datos suficientes para calcular throughput");
    }
    
    // ========== ESTADÍSTICAS DE CONSUMO ENERGÉTICO ==========
    NS_LOG_INFO("---------- CONSUMO ENERGÉTICO ----------");
    
    if (g_transmissionCount > 0)
    {
        g_energyPerTransmission = g_totalEnergyConsumed / g_transmissionCount;
        
        // Calcular estadísticas adicionales
        double minEnergy = *std::min_element(g_energyConsumptions.begin(), g_energyConsumptions.end());
        double maxEnergy = *std::max_element(g_energyConsumptions.begin(), g_energyConsumptions.end());
        
        // Calcular desviación estándar
        double sumEnergy = 0.0;
        for (double e : g_energyConsumptions) sumEnergy += e;
        double avgEnergy = sumEnergy / g_energyConsumptions.size();
        
        double varianceEnergy = 0.0;
        for (double e : g_energyConsumptions)
        {
            varianceEnergy += (e - avgEnergy) * (e - avgEnergy);
        }
        double stdDevEnergy = std::sqrt(varianceEnergy / g_energyConsumptions.size());
        
        // Estimar autonomía con batería típica (2600 mAh a 3.7V = 9.62 Wh = 34632 J)
        double batteryCapacity = 34632.0; // Joules
        double estimatedTransmissions = batteryCapacity / g_energyPerTransmission;
        double autonomyHours = (estimatedTransmissions * 60) / 3600; // Asumiendo 1 tx/minuto
        
        NS_LOG_INFO("Total transmisiones: " << g_transmissionCount);
        NS_LOG_INFO("Energía total consumida: " << g_totalEnergyConsumed * 1000 << " mJ");
        NS_LOG_INFO("Energía total consumida: " << g_totalEnergyConsumed << " J");
        NS_LOG_INFO("Energía por transmisión (promedio): " << g_energyPerTransmission * 1000 << " mJ");
        NS_LOG_INFO("Energía por transmisión (mínima): " << minEnergy * 1000 << " mJ");
        NS_LOG_INFO("Energía por transmisión (máxima): " << maxEnergy * 1000 << " mJ");
        NS_LOG_INFO("Desviación estándar: " << stdDevEnergy * 1000 << " mJ");
        NS_LOG_INFO("Transmisiones estimadas con batería 2600mAh: " << (int)estimatedTransmissions);
        NS_LOG_INFO("Autonomía estimada (1 tx/min): " << autonomyHours << " horas");
        
        // Calcular eficiencia energética
        if (g_totalBytesReceived > 0)
        {
            double energyPerByte = (g_totalEnergyConsumed * 1000) / g_totalBytesReceived; // mJ/byte
            double energyPerBit = energyPerByte / 8.0; // mJ/bit
            NS_LOG_INFO("Eficiencia energética: " << energyPerBit << " mJ/bit");
        }
    }
    else
    {
        NS_LOG_INFO("No hay datos de transmisiones para calcular energía");
    }
    
    std::ofstream csvFile;
    // ✅ NOMBRES DEFINITIVOS - 100% ÚNICOS PARA SALINAS 3GW
    std::string csvFileName = g_enableP2P ? "resultados_salinas_movil_3gw_p2p.csv" : "resultados_salinas_movil_3gw_base.csv";
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
        
        // Calcular eficiencia P2P
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
        NS_LOG_INFO("Resultados exportados a: " << csvFileName);
    }
    
    Simulator::Destroy();
    g_posFile.close();
    g_coberturaFile.close();
    
    std::cout << "\n✅ SIMULACIÓN SALINAS 3GW FINALIZADA" << std::endl;
    std::cout << "📁 Archivos generados:" << std::endl;
    std::cout << "   positions_salinas_movil_3gw.csv" << std::endl;
    std::cout << "   cobertura_salinas_movil_3gw.csv" << std::endl;
    std::cout << "   " << csvFileName << std::endl;
    std::cout << "   salinas-mobile-3gw-anim.xml" << std::endl;
    
    NS_LOG_INFO("✓ Archivos generados:");
    NS_LOG_INFO("  - positions_salinas_movil_3gw.csv");
    NS_LOG_INFO("  - cobertura_salinas_movil_3gw.csv");
    NS_LOG_INFO("  - " << csvFileName);
    NS_LOG_INFO("  - salinas-mobile-3gw-anim.xml");
    
    NS_LOG_INFO("Simulación Salinas Mobile 3GW finalizada");
    return 0;
}

