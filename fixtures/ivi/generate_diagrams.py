#!/usr/bin/env python3
"""
Generate IVI System Architecture and Data Flow Diagrams as PNG images.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
import numpy as np
import os

# Set font for Chinese support
plt.rcParams['font.family'] = ['DejaVu Sans', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def draw_system_architecture():
    """Generate IVI System Architecture Diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('IVI System Architecture Diagram', fontsize=16, fontweight='bold', pad=20)

    # Colors
    colors = {
        'external': '#ffcccc',      # Light red - external/untrusted
        'hardware': '#cce5ff',      # Light blue - hardware
        'software': '#d4edda',      # Light green - software
        'security': '#fff3cd',      # Light yellow - security
        'vehicle': '#e2d5f1',       # Light purple - vehicle network
        'boundary': '#333333',      # Dark - trust boundary
    }

    # === Trust Boundaries ===
    # External World boundary
    ax.add_patch(FancyBboxPatch((0.3, 8.5), 15.4, 3.2, boxstyle="round,pad=0.1",
                                 facecolor='none', edgecolor=colors['boundary'],
                                 linestyle='--', linewidth=2))
    ax.text(8, 11.5, 'External World (Untrusted)', ha='center', fontsize=10, style='italic')

    # IVI System boundary
    ax.add_patch(FancyBboxPatch((0.3, 2.8), 15.4, 5.5, boxstyle="round,pad=0.1",
                                 facecolor='none', edgecolor=colors['boundary'],
                                 linestyle='-', linewidth=2))
    ax.text(8, 8.1, 'IVI Head Unit (SA8155P)', ha='center', fontsize=10, fontweight='bold')

    # Vehicle Network boundary
    ax.add_patch(FancyBboxPatch((0.3, 0.3), 15.4, 2.3, boxstyle="round,pad=0.1",
                                 facecolor='none', edgecolor=colors['boundary'],
                                 linestyle='-.', linewidth=2))
    ax.text(8, 2.4, 'Vehicle Network', ha='center', fontsize=10, style='italic')

    def draw_box(x, y, w, h, label, color, sublabel=None):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                                     facecolor=color, edgecolor='black', linewidth=1.5))
        ax.text(x + w/2, y + h/2 + (0.15 if sublabel else 0), label,
                ha='center', va='center', fontsize=8, fontweight='bold')
        if sublabel:
            ax.text(x + w/2, y + h/2 - 0.2, sublabel, ha='center', va='center', fontsize=6)

    def draw_arrow(start, end, color='black', style='->', label=None, curved=False):
        if curved:
            arrow = FancyArrowPatch(start, end, arrowstyle=style,
                                    connectionstyle="arc3,rad=0.2",
                                    color=color, linewidth=1.5)
        else:
            arrow = FancyArrowPatch(start, end, arrowstyle=style,
                                    color=color, linewidth=1.5)
        ax.add_patch(arrow)
        if label:
            mid = ((start[0] + end[0])/2, (start[1] + end[1])/2 + 0.2)
            ax.text(mid[0], mid[1], label, fontsize=6, ha='center',
                   bbox=dict(boxstyle='round', facecolor='white', edgecolor='none', alpha=0.8))

    # === External Interfaces (Top) ===
    draw_box(0.5, 9, 2, 1.2, 'WiFi', colors['external'], '802.11ax')
    draw_box(3, 9, 2, 1.2, 'Bluetooth', colors['external'], 'BT 5.1')
    draw_box(5.5, 9, 2, 1.2, '4G/LTE', colors['external'], 'Cellular')
    draw_box(8, 9, 2, 1.2, 'GNSS', colors['external'], 'GPS/GLONASS')
    draw_box(10.5, 9, 2, 1.2, 'USB', colors['external'], 'USB 2.0')
    draw_box(13, 9, 2.5, 1.2, 'Debug', colors['external'], 'UART/JTAG')

    # === Software Layer ===
    # Android OS
    draw_box(1, 6.5, 3.5, 1.2, 'Android 12', colors['software'], 'AAOS')
    # Apps
    draw_box(5, 6.5, 2, 1.2, 'Navigation', colors['software'])
    draw_box(7.2, 6.5, 2, 1.2, 'Media', colors['software'])
    draw_box(9.4, 6.5, 2, 1.2, 'Phone', colors['software'])
    draw_box(11.6, 6.5, 2, 1.2, 'Browser', colors['software'])
    draw_box(13.8, 6.5, 1.7, 1.2, 'OTA', colors['software'])

    # Services Layer
    draw_box(1, 4.8, 3.5, 1.2, 'Vehicle HAL', colors['software'], 'HIDL')
    draw_box(5, 4.8, 4, 1.2, 'Android Framework', colors['software'], 'Binder IPC')
    draw_box(9.5, 4.8, 3, 1.2, 'Location Svc', colors['software'])
    draw_box(13, 4.8, 2.5, 1.2, 'Audio Svc', colors['software'])

    # Kernel & Security
    draw_box(1, 3.1, 5, 1.2, 'Linux Kernel 5.4', colors['software'], 'SELinux')
    draw_box(6.5, 3.1, 3, 1.2, 'TEE', colors['security'], 'TrustZone')
    draw_box(10, 3.1, 2.5, 1.2, 'HSM', colors['security'], 'SLI97')
    draw_box(13, 3.1, 2.5, 1.2, 'Crypto', colors['security'], 'AES/RSA')

    # === Vehicle Network Components (Bottom) ===
    draw_box(1, 0.6, 2.5, 1.2, 'CAN Bus', colors['vehicle'], 'TJA1043')
    draw_box(4, 0.6, 2.5, 1.2, 'Ethernet', colors['vehicle'], '100BASE-T1')
    draw_box(7, 0.6, 2.5, 1.2, 'Gateway', colors['vehicle'])
    draw_box(10, 0.6, 2.5, 1.2, 'BCM', colors['vehicle'])
    draw_box(13, 0.6, 2.5, 1.2, 'Cluster', colors['vehicle'])

    # === Connections ===
    # External to Software
    draw_arrow((1.5, 9), (2.5, 7.7), label='WPA3')
    draw_arrow((4, 9), (10.4, 7.7), label='SSP')
    draw_arrow((6.5, 9), (14.5, 7.7), label='TLS')
    draw_arrow((9, 9), (6, 7.7), label='NMEA')
    draw_arrow((11.5, 9), (8.2, 7.7), label='MTP')

    # Software internal
    draw_arrow((2.75, 6.5), (2.75, 6), style='->')
    draw_arrow((7, 6.5), (7, 6), style='->')
    draw_arrow((3.5, 5.4), (5, 5.4), style='<->')

    # To Vehicle Network
    draw_arrow((2.75, 4.8), (2.25, 1.8), label='CAN')
    draw_arrow((2.75, 4.8), (5.25, 1.8), label='DoIP')

    # Legend
    legend_y = 11.2
    ax.add_patch(Rectangle((0.5, legend_y), 0.3, 0.3, facecolor=colors['external']))
    ax.text(0.9, legend_y + 0.15, 'External Interface', fontsize=7, va='center')
    ax.add_patch(Rectangle((3, legend_y), 0.3, 0.3, facecolor=colors['software']))
    ax.text(3.4, legend_y + 0.15, 'Software', fontsize=7, va='center')
    ax.add_patch(Rectangle((5.2, legend_y), 0.3, 0.3, facecolor=colors['security']))
    ax.text(5.6, legend_y + 0.15, 'Security', fontsize=7, va='center')
    ax.add_patch(Rectangle((7.2, legend_y), 0.3, 0.3, facecolor=colors['vehicle']))
    ax.text(7.6, legend_y + 0.15, 'Vehicle Network', fontsize=7, va='center')

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'ivi_system_architecture.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Generated: {output_path}")


def draw_data_flow_diagram():
    """Generate IVI Data Flow Diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('IVI Data Flow Diagram (DFD)', fontsize=16, fontweight='bold', pad=20)

    colors = {
        'process': '#cce5ff',
        'datastore': '#fff3cd',
        'external': '#f8d7da',
        'data_high': '#dc3545',
        'data_medium': '#fd7e14',
        'data_low': '#28a745',
    }

    def draw_process(x, y, r, label):
        """Draw a process (circle)"""
        circle = Circle((x, y), r, facecolor=colors['process'], edgecolor='black', linewidth=2)
        ax.add_patch(circle)
        ax.text(x, y, label, ha='center', va='center', fontsize=8, fontweight='bold',
               wrap=True)

    def draw_external(x, y, w, h, label):
        """Draw external entity (rectangle)"""
        ax.add_patch(Rectangle((x, y), w, h, facecolor=colors['external'],
                               edgecolor='black', linewidth=2))
        ax.text(x + w/2, y + h/2, label, ha='center', va='center', fontsize=8, fontweight='bold')

    def draw_datastore(x, y, w, h, label):
        """Draw data store (open rectangle)"""
        ax.plot([x, x+w], [y+h, y+h], 'k-', linewidth=2)
        ax.plot([x, x+w], [y, y], 'k-', linewidth=2)
        ax.add_patch(Rectangle((x, y), w, h, facecolor=colors['datastore'],
                               edgecolor='none'))
        ax.text(x + w/2, y + h/2, label, ha='center', va='center', fontsize=7)

    def draw_flow(start, end, label, sensitivity='low', curved=0):
        """Draw data flow arrow with sensitivity color"""
        color = colors[f'data_{sensitivity}']
        style = f'Simple, tail_width=0.5, head_width=4, head_length=5'
        if curved:
            arrow = FancyArrowPatch(start, end, arrowstyle='->', color=color,
                                    connectionstyle=f"arc3,rad={curved}",
                                    linewidth=2, mutation_scale=15)
        else:
            arrow = FancyArrowPatch(start, end, arrowstyle='->', color=color,
                                    linewidth=2, mutation_scale=15)
        ax.add_patch(arrow)
        mid = ((start[0] + end[0])/2, (start[1] + end[1])/2)
        ax.text(mid[0], mid[1] + 0.3, label, fontsize=6, ha='center',
               bbox=dict(boxstyle='round', facecolor='white', edgecolor=color, alpha=0.9))

    # === External Entities ===
    draw_external(0.2, 7.5, 2, 1.2, 'Mobile\nDevice')
    draw_external(0.2, 5, 2, 1.2, 'Cloud\nBackend')
    draw_external(0.2, 2.5, 2, 1.2, 'GNSS\nSatellite')
    draw_external(13.8, 7.5, 2, 1.2, 'Vehicle\nGateway')
    draw_external(13.8, 5, 2, 1.2, 'BCM')
    draw_external(13.8, 2.5, 2, 1.2, 'Cluster')

    # === Processes ===
    draw_process(4.5, 8, 1, 'Bluetooth\nService')
    draw_process(4.5, 5.5, 1, 'OTA\nService')
    draw_process(4.5, 3, 1, 'Location\nService')
    draw_process(8, 8, 1.2, 'Phone\nApp')
    draw_process(8, 5.5, 1.2, 'Navigation\nApp')
    draw_process(8, 3, 1.2, 'Media\nPlayer')
    draw_process(11.5, 6.5, 1, 'Vehicle\nHAL')
    draw_process(11.5, 3.5, 1, 'CAN\nDriver')

    # === Data Stores ===
    draw_datastore(5.8, 0.3, 2.4, 0.8, 'D1: User Contacts')
    draw_datastore(8.5, 0.3, 2.4, 0.8, 'D2: Location History')
    draw_datastore(11.2, 0.3, 2.4, 0.8, 'D3: Firmware')
    draw_datastore(2.8, 0.3, 2.7, 0.8, 'D4: Media Files')

    # === Data Flows ===
    # Bluetooth flows
    draw_flow((2.2, 8.1), (3.5, 8.1), 'BT Pairing', 'medium')
    draw_flow((5.5, 8), (6.8, 8), 'Contacts', 'high')
    draw_flow((7, 7.2), (7, 1.1), 'Sync', 'high', curved=-0.3)

    # Cloud/OTA flows
    draw_flow((2.2, 5.6), (3.5, 5.6), 'TLS/HTTPS', 'medium')
    draw_flow((5.5, 5.2), (12, 1.1), 'FW Update', 'high', curved=-0.2)

    # GPS flows
    draw_flow((2.2, 3.1), (3.5, 3.1), 'NMEA', 'low')
    draw_flow((5.5, 3.2), (6.8, 5.2), 'Position', 'medium')
    draw_flow((8, 4.3), (9.5, 1.1), 'History', 'medium', curved=0.2)

    # Navigation to Cluster
    draw_flow((9.2, 5.5), (10.5, 6.2), 'Guidance', 'low')
    draw_flow((12.5, 6.2), (13.8, 5.6), 'Display', 'low')
    draw_flow((12.5, 3.5), (13.8, 3.1), 'Icons', 'low')

    # Vehicle HAL flows
    draw_flow((12.5, 7), (13.8, 7.8), 'CAN Cmd', 'high')
    draw_flow((11.5, 5.5), (11.5, 4.5), 'Signals', 'medium')

    # Media
    draw_flow((8, 2), (5, 1.1), 'Playback', 'low', curved=0.2)

    # Legend
    ax.text(0.5, 9.5, 'Data Sensitivity:', fontsize=9, fontweight='bold')
    ax.plot([2.5, 3.2], [9.5, 9.5], color=colors['data_high'], linewidth=3)
    ax.text(3.4, 9.5, 'High (PII/Critical)', fontsize=7, va='center')
    ax.plot([6, 6.7], [9.5, 9.5], color=colors['data_medium'], linewidth=3)
    ax.text(6.9, 9.5, 'Medium', fontsize=7, va='center')
    ax.plot([8.8, 9.5], [9.5, 9.5], color=colors['data_low'], linewidth=3)
    ax.text(9.7, 9.5, 'Low', fontsize=7, va='center')

    # Shape legend
    ax.add_patch(Circle((12, 9.5), 0.25, facecolor=colors['process'], edgecolor='black'))
    ax.text(12.4, 9.5, 'Process', fontsize=7, va='center')
    ax.add_patch(Rectangle((13.5, 9.3), 0.5, 0.4, facecolor=colors['external'], edgecolor='black'))
    ax.text(14.1, 9.5, 'External Entity', fontsize=7, va='center')

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'ivi_data_flow_diagram.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Generated: {output_path}")


def draw_attack_tree():
    """Generate Attack Tree Diagram for IVI"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('IVI Attack Tree - Remote Vehicle Control', fontsize=14, fontweight='bold', pad=20)

    colors = {
        'goal': '#dc3545',
        'or': '#fd7e14',
        'and': '#007bff',
        'leaf': '#28a745',
    }

    def draw_node(x, y, w, h, label, color, node_type=''):
        ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.05",
                                     facecolor=color, edgecolor='black', linewidth=1.5, alpha=0.8))
        ax.text(x, y, label, ha='center', va='center', fontsize=7, fontweight='bold', wrap=True)
        if node_type:
            ax.text(x, y-h/2-0.15, node_type, ha='center', va='top', fontsize=6,
                   style='italic', color='gray')

    def connect(parent, child):
        ax.plot([parent[0], child[0]], [parent[1], child[1]], 'k-', linewidth=1.5)

    # Root Goal
    draw_node(8, 9, 4, 0.8, 'Unauthorized Vehicle Control', colors['goal'], 'GOAL')

    # Level 1 - OR
    draw_node(4, 7, 3, 0.7, 'Compromise IVI', colors['or'], 'OR')
    draw_node(12, 7, 3, 0.7, 'Compromise T-BOX', colors['or'], 'OR')
    connect((8, 8.6), (4, 7.35))
    connect((8, 8.6), (12, 7.35))

    # Level 2 - IVI attacks
    draw_node(1.5, 5, 2.5, 0.7, 'Bluetooth RCE', colors['or'], 'OR')
    draw_node(4, 5, 2.5, 0.7, 'Malicious App', colors['or'], 'OR')
    draw_node(6.5, 5, 2.5, 0.7, 'USB Attack', colors['or'], 'OR')
    connect((4, 6.65), (1.5, 5.35))
    connect((4, 6.65), (4, 5.35))
    connect((4, 6.65), (6.5, 5.35))

    # Level 2 - T-BOX attacks
    draw_node(10, 5, 2.5, 0.7, 'Fake Base Station', colors['or'], 'OR')
    draw_node(12.5, 5, 2.5, 0.7, 'FOTA Hijack', colors['and'], 'AND')
    draw_node(15, 5, 2, 0.7, 'APN Leak', colors['leaf'])
    connect((12, 6.65), (10, 5.35))
    connect((12, 6.65), (12.5, 5.35))
    connect((12, 6.65), (15, 5.35))

    # Level 3 - Bluetooth
    draw_node(0.5, 3, 2, 0.6, 'CVE-2022-\n20345', colors['leaf'])
    draw_node(2.5, 3, 2, 0.6, 'Protocol\nFuzzing', colors['leaf'])
    connect((1.5, 4.65), (0.5, 3.3))
    connect((1.5, 4.65), (2.5, 3.3))

    # Level 3 - Malicious App
    draw_node(3, 3, 1.8, 0.6, 'Sideload\nAPK', colors['leaf'])
    draw_node(5, 3, 1.8, 0.6, 'Exploit\nWebView', colors['leaf'])
    connect((4, 4.65), (3, 3.3))
    connect((4, 4.65), (5, 3.3))

    # Level 3 - USB
    draw_node(6, 3, 1.8, 0.6, 'BadUSB\nPayload', colors['leaf'])
    draw_node(7.8, 3, 1.8, 0.6, 'Media\nFile Exploit', colors['leaf'])
    connect((6.5, 4.65), (6, 3.3))
    connect((6.5, 4.65), (7.8, 3.3))

    # Level 3 - Fake Base Station
    draw_node(9.2, 3, 2, 0.6, '2G\nDowngrade', colors['leaf'])
    draw_node(11.2, 3, 2, 0.6, 'SMS\nInjection', colors['leaf'])
    connect((10, 4.65), (9.2, 3.3))
    connect((10, 4.65), (11.2, 3.3))

    # Level 3 - FOTA (AND)
    draw_node(12.5, 3, 2, 0.6, 'DNS\nSpoofing', colors['leaf'])
    draw_node(14.5, 3, 2, 0.6, 'No Sig\nVerify', colors['leaf'])
    connect((12.5, 4.65), (12.5, 3.3))
    connect((12.5, 4.65), (14.5, 3.3))

    # Level 4 - Post exploitation
    draw_node(4, 1.2, 3.5, 0.6, 'Lateral Movement to CAN', colors['or'], 'OR')
    connect((4, 2.7), (4, 1.5))

    draw_node(2, 0.3, 2, 0.5, 'Unlock\nDoors', colors['leaf'])
    draw_node(4, 0.3, 2, 0.5, 'Start\nEngine', colors['leaf'])
    draw_node(6, 0.3, 2, 0.5, 'Disable\nBrakes', colors['leaf'])
    connect((4, 0.9), (2, 0.55))
    connect((4, 0.9), (4, 0.55))
    connect((4, 0.9), (6, 0.55))

    # Legend
    ax.add_patch(Rectangle((10, 0.8), 0.4, 0.3, facecolor=colors['goal']))
    ax.text(10.5, 0.95, 'Attack Goal', fontsize=7, va='center')
    ax.add_patch(Rectangle((10, 0.3), 0.4, 0.3, facecolor=colors['or']))
    ax.text(10.5, 0.45, 'OR Node', fontsize=7, va='center')
    ax.add_patch(Rectangle((12.5, 0.8), 0.4, 0.3, facecolor=colors['and']))
    ax.text(13, 0.95, 'AND Node', fontsize=7, va='center')
    ax.add_patch(Rectangle((12.5, 0.3), 0.4, 0.3, facecolor=colors['leaf']))
    ax.text(13, 0.45, 'Leaf (Attack Step)', fontsize=7, va='center')

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'ivi_attack_tree.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Generated: {output_path}")


def draw_trust_boundary_diagram():
    """Generate Trust Boundary Diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('IVI Trust Boundary Model', fontsize=14, fontweight='bold', pad=20)

    # Trust levels (nested rectangles)
    levels = [
        (0.5, 0.5, 13, 9, '#ffebee', 'Level 0: External World (Untrusted)', '--'),
        (1.5, 1.5, 11, 7, '#fff3e0', 'Level 1: IVI User Space', '-'),
        (2.5, 2.5, 9, 5, '#e8f5e9', 'Level 2: Kernel Space', '-'),
        (3.5, 3.5, 7, 3, '#e3f2fd', 'Level 3: TrustZone (Secure World)', '-'),
    ]

    for x, y, w, h, color, label, style in levels:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                                     facecolor=color, edgecolor='black',
                                     linestyle=style, linewidth=2))
        ax.text(x + 0.2, y + h - 0.3, label, fontsize=9, fontweight='bold')

    # Components at each level
    def draw_component(x, y, w, h, label, color='white'):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03",
                                     facecolor=color, edgecolor='black', linewidth=1))
        ax.text(x + w/2, y + h/2, label, ha='center', va='center', fontsize=7)

    # Level 0 - External
    draw_component(0.8, 8, 1.5, 0.7, 'Internet')
    draw_component(2.5, 8, 1.5, 0.7, 'BT Device')
    draw_component(4.2, 8, 1.5, 0.7, 'USB Stick')
    draw_component(10.5, 8, 2, 0.7, 'OBD-II Port')

    # Level 1 - User Space
    draw_component(2, 6, 1.8, 0.8, 'Browser', '#c8e6c9')
    draw_component(4, 6, 1.8, 0.8, 'Nav App', '#c8e6c9')
    draw_component(6, 6, 1.8, 0.8, 'Phone App', '#c8e6c9')
    draw_component(8, 6, 1.8, 0.8, '3rd Party', '#ffcdd2')
    draw_component(10, 6, 1.8, 0.8, 'OTA Svc', '#c8e6c9')

    # Level 2 - Kernel
    draw_component(3, 4, 2.5, 0.8, 'Linux Kernel', '#bbdefb')
    draw_component(6, 4, 2.5, 0.8, 'Device Drivers', '#bbdefb')
    draw_component(9, 4, 2.5, 0.8, 'SELinux', '#90caf9')

    # Level 3 - Secure World
    draw_component(4.5, 3.7, 2, 0.6, 'TEE OS', '#64b5f6')
    draw_component(7, 3.7, 2, 0.6, 'Keymaster', '#64b5f6')
    draw_component(9.2, 3.7, 1.5, 0.6, 'HSM', '#42a5f5')

    # Arrows showing boundary crossings
    ax.annotate('', xy=(2, 7.8), xytext=(2.5, 6.8),
                arrowprops=dict(arrowstyle='->', color='red', lw=2))
    ax.text(1.2, 7.3, 'Web\nTraffic', fontsize=6, color='red')

    ax.annotate('', xy=(4.5, 5.2), xytext=(4.5, 4.8),
                arrowprops=dict(arrowstyle='->', color='blue', lw=2))
    ax.text(4.7, 5, 'Syscall', fontsize=6, color='blue')

    ax.annotate('', xy=(8, 4), xytext=(8, 4.3),
                arrowprops=dict(arrowstyle='<->', color='green', lw=2))
    ax.text(8.2, 4.15, 'SMC', fontsize=6, color='green')

    # Risk annotations
    ax.text(12, 6.5, 'High Risk:\n- Malicious Apps\n- Browser Exploits', fontsize=7,
           bbox=dict(boxstyle='round', facecolor='#ffcdd2'))
    ax.text(12, 4.5, 'Medium Risk:\n- Kernel Vulns\n- Driver Bugs', fontsize=7,
           bbox=dict(boxstyle='round', facecolor='#fff9c4'))
    ax.text(12, 2.5, 'Low Risk:\n- HSM Protected\n- Keys Isolated', fontsize=7,
           bbox=dict(boxstyle='round', facecolor='#c8e6c9'))

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'ivi_trust_boundaries.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Generated: {output_path}")


if __name__ == '__main__':
    print("Generating IVI diagrams...")
    draw_system_architecture()
    draw_data_flow_diagram()
    draw_attack_tree()
    draw_trust_boundary_diagram()
    print("\nAll diagrams generated successfully!")
