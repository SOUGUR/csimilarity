import numpy as np
import os
from .models import NameVector
from django.conf import settings
import matplotlib
import time

matplotlib.use('Agg')  

import matplotlib.pyplot as plt

#returns index of character stating from 1
def alphabet_index(c):
    return ord(c.lower()) - 96


def calculate_xy(name):
    name = name.lower()
    freq = [0]*26

    for c in name:

        if c.isalpha():

            freq[ord(c)-97]+=1

    # sum of frequencies of characters
    x = sum(f*f for f in freq)

    # position index multiplied by characters position
    y = sum((i+1)*alphabet_index(c)
            for i,c in enumerate(name)
            if c.isalpha())


    return x,y


def get_or_create_vector(name):

    obj = NameVector.objects.filter(
        name=name
    ).first()


    if obj:

        return obj.x,obj.y


    x,y = calculate_xy(name)


    NameVector.objects.create(
        name=name,
        x=x,
        y=y
    )


    return x,y

def letter_similarity(n1,n2):

    f1=[0]*26
    f2=[0]*26

    for c in n1.lower():

        if c.isalpha():

            f1[ord(c)-97]+=1


    for c in n2.lower():

        if c.isalpha():

            f2[ord(c)-97]+=1


    diff=sum(abs(a-b) for a,b in zip(f1,f2))

    max_sum=sum(f1)+sum(f2)

    return 1-diff/max_sum


def distance(p1,p2):
    return np.sqrt(
        (p1[0]-p2[0])**2 +
        (p1[1]-p2[1])**2
    )


def similarity_score(n1,n2,p1,p2):

    L = letter_similarity(n1,n2)

    d = distance(p1,p2)

    D = np.exp(-d/50)

    return 0.7*D + 0.3*L



def generate_plot(names, get_vector_func, similarity_func):
    data = []
    for name in names:
        x, y = get_vector_func(name)
        
        # 1. Radius (r): Use complexity/length (how "heavy" the name is)
        # We use a log or square root to keep long names from flying off the chart
        r = np.sqrt(np.sqrt(x*x + y*y))
        
        # 2. Angle (theta): Use the "Average Character Value" 
        # This determines the "Flavor" or "Direction" of the name (A-names vs Z-names)
        chars = [ord(c.lower()) - 96 for c in name if c.isalpha()]
        avg_char = sum(chars) / len(chars) if chars else 0
        
        # Map average char (1-26) to 0-360 degrees (0 to 2*pi)
        theta = (avg_char / 26) * 2 * np.pi
        
        data.append({'name': name, 'r': r, 'theta': theta, 'x': x, 'y': y})

    # DARK THEME RADAR PLOT
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(10, 10), facecolor='#0b0f0b')
    ax = fig.add_subplot(111, projection='polar')
    ax.set_facecolor('#0f130f')
    
    # Grid Styling
    ax.grid(True, color='#2a8c5e', linestyle='--', alpha=0.3)
    ax.spines['polar'].set_color('#2a8c5e')
    
    # 1. Similarity Connections
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            n1, p1 = data[i]['name'], (data[i]['x'], data[i]['y'])
            n2, p2 = data[j]['name'], (data[j]['x'], data[j]['y'])
            score = similarity_func(n1, n2, p1, p2)
            
            if score > 0.4:
                ax.plot([data[i]['theta'], data[j]['theta']], 
                        [data[i]['r'], data[j]['r']], 
                        color=(0,score,0), alpha=score*0.4, linewidth=score*3, zorder=1)

    # 2. Plot Points & Labels
    max_r = max([d['r'] for d in data]) if data else 1
    for entry in data:
        ax.scatter(entry['theta'], entry['r'], s=150, c='#2ecc71', 
                   edgecolors='#b3ffcf', linewidth=1, zorder=3, alpha=0.9)
        
        # Label offset
        ax.text(entry['theta'], entry['r'] + (max_r * 0.07), 
                entry['name'].upper(), color='#b3ffcf', fontsize=10, 
                fontweight='bold', ha='center',
                bbox=dict(facecolor='#0f130f', alpha=0.8, edgecolor='#2a8c5e', boxstyle='round,pad=0.3'),
                zorder=4)
        
        ax.plot(
            [entry['theta'],entry['theta']],
            [0,entry['r']],
            color='#2ecc71',
            alpha=0.2
            )

    plt.title("NAME::VECTOR RADAR PROJECTION", color='#2ecc71', fontsize=16, pad=40)
    
    # Aesthetics
    ax.set_yticklabels([]) # Hide distance numbers for cleaner look
    angles = np.linspace(0, 2*np.pi, 8, endpoint=False)

    ax.set_xticks(angles)

    ax.set_xticklabels(
    [
    'COMPOSITION A',
    '',
    'COMPOSITION B',
    '',
    'COMPOSITION C',
    '',
    'COMPOSITION D',
    ''
    ],
    color='#5faf7a'
    )

    # File Save
    folder = os.path.join(settings.MEDIA_ROOT, "plots")
    os.makedirs(folder, exist_ok=True)
    filename = f"radar_{int(time.time())}.png"
    file_path = os.path.join(folder, filename)
    plt.savefig(file_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close()

    return f"media/plots/{filename}"