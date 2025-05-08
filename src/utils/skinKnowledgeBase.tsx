/**
 * Skin Knowledge Base
 * 
 * This file contains skincare information that can be referenced by the LLM
 * to provide more accurate and helpful responses.
 */

// Sample product recommendations by skin type
const productsByType = {
  dry: {
    cleansers: [
      { name: "CeraVe Hydrating Facial Cleanser", description: "super gentle and hydrating" },
      { name: "La Roche-Posay Toleriane Hydrating Gentle Cleanser", description: "perfect for sensitive dry skin" },
      { name: "Neutrogena Ultra Gentle Hydrating Cleanser", description: "affordable and effective" },
    ],
    moisturizers: [
      { name: "CeraVe Moisturizing Cream", description: "rich but non-greasy" },
      { name: "First Aid Beauty Ultra Repair Cream", description: "intensive hydration" },
      { name: "Weleda Skin Food", description: "great for extra dry patches" },
    ],
    serums: [
      { name: "The Ordinary Hyaluronic Acid 2% + B5", description: "intense hydration booster" },
      { name: "Vichy Minéral 89", description: "hydrating and strengthening" },
      { name: "La Roche-Posay Hyalu B5 Serum", description: "replenishing and plumping" },
    ]
  },
  oily: {
    cleansers: [
      { name: "CeraVe Foaming Facial Cleanser", description: "balances without over-drying" },
      { name: "La Roche-Posay Effaclar Purifying Foaming Gel", description: "great for oily skin" },
      { name: "Neutrogena Oil-Free Acne Wash", description: "helps with breakouts too" },
    ],
    moisturizers: [
      { name: "Neutrogena Hydro Boost Water Gel", description: "lightweight hydration" },
      { name: "The Ordinary Natural Moisturizing Factors", description: "non-greasy formula" },
      { name: "Clinique Dramatically Different Moisturizing Gel", description: "oil-free option" },
    ],
    serums: [
      { name: "The Ordinary Niacinamide 10% + Zinc 1%", description: "controls sebum production" },
      { name: "Paula's Choice 2% BHA Liquid Exfoliant", description: "unclogs pores" },
      { name: "Caudalie Vinopure Serum", description: "mattifying and clarifying" },
    ]
  },
  normal: {
    cleansers: [
      { name: "Cetaphil Gentle Skin Cleanser", description: "a perfect balance for normal skin" },
      { name: "Kiehl's Ultra Facial Cleanser", description: "maintains natural moisture balance" },
      { name: "Fresh Soy Face Cleanser", description: "gentle and effective" },
    ],
    moisturizers: [
      { name: "CeraVe Daily Moisturizing Lotion", description: "balanced hydration" },
      { name: "Cetaphil Daily Hydrating Lotion", description: "light but effective" },
      { name: "Kiehl's Ultra Facial Cream", description: "perfect all-season option" },
    ],
    serums: [
      { name: "The Ordinary Buffet", description: "multi-peptide anti-aging serum" },
      { name: "Glossier Super Bounce", description: "hydrating hyaluronic acid and vitamin B5" },
      { name: "Drunk Elephant B-Hydra Intensive Hydration Serum", description: "lightweight and balancing" },
    ]
  }
};

// Products by skin issue
const productsByIssue = {
  acne: [
    { name: "Paula's Choice 2% BHA Liquid Exfoliant", description: "gentle but effective" },
    { name: "The Ordinary Niacinamide 10% + Zinc 1%", description: "helps reduce breakouts" },
    { name: "La Roche-Posay Effaclar Duo", description: "targets blemishes without overdrying" },
    { name: "Differin Gel", description: "prescription-strength retinoid now available OTC" },
    { name: "CeraVe Acne Foaming Cream Cleanser", description: "with benzoyl peroxide" },
  ],
  redness: [
    { name: "Dr. Jart+ Cicapair Tiger Grass Color Correcting Treatment", description: "calms and covers redness" },
    { name: "Avène Antirougeurs Calm Soothing Repair Mask", description: "intensive treatment" },
    { name: "The Ordinary Azelaic Acid Suspension", description: "helps reduce inflammation" },
    { name: "La Roche-Posay Rosaliac AR Intense", description: "visible redness reducing serum" },
    { name: "Eucerin Redness Relief Night Cream", description: "soothes and hydrates overnight" },
  ],
  bags: [
    { name: "The Ordinary Caffeine Solution 5% + EGCG", description: "reduces puffiness" },
    { name: "CeraVe Eye Repair Cream", description: "gentle but effective" },
    { name: "Neutrogena Hydro Boost Eye Gel-Cream", description: "hydrating and refreshing" },
    { name: "ROC Retinol Correxion Eye Cream", description: "targets fine lines and dark circles" },
    { name: "Kiehl's Creamy Eye Treatment with Avocado", description: "rich hydration for dry under-eyes" },
  ],
  aging: [
    { name: "Olay Regenerist Micro-Sculpting Cream", description: "affordable anti-aging" },
    { name: "Neutrogena Rapid Wrinkle Repair", description: "with retinol" },
    { name: "The Ordinary Granactive Retinoid 2% Emulsion", description: "gentle retinoid formula" },
    { name: "CeraVe Skin Renewing Night Cream", description: "with peptides" },
    { name: "L'Oreal Paris Revitalift Night Serum with Pure Retinol", description: "potent anti-aging" },
  ],
  dryness: [
    { name: "Aquaphor Healing Ointment", description: "intense moisture for very dry skin" },
    { name: "Neutrogena Hydro Boost Gel-Cream", description: "with hyaluronic acid" },
    { name: "La Roche-Posay Lipikar Balm AP+", description: "for extremely dry skin" },
    { name: "Kiehl's Ultra Facial Deep Moisture Balm", description: "rich texture for deep hydration" },
    { name: "First Aid Beauty Ultra Repair Cream", description: "head-to-toe moisture" },
  ]
};

// Sunscreens (important for everyone)
const sunscreens = [
  { name: "Supergoop! Unseen Sunscreen SPF 40", description: "invisible finish" },
  { name: "La Roche-Posay Anthelios Melt-In Milk SPF 60", description: "great protection" },
  { name: "EltaMD UV Clear Broad-Spectrum SPF 46", description: "dermatologist favorite" },
  { name: "Neutrogena Ultra Sheer Dry-Touch SPF 100+", description: "high protection, non-greasy" },
  { name: "Black Girl Sunscreen SPF 30", description: "no white cast, moisturizing" },
];

// Skincare routines by type
const routines = {
  dry: {
    morning: [
      "1. **Cleanse** with a hydrating, non-foaming cleanser",
      "2. **Apply a hydrating serum** with hyaluronic acid while skin is still damp",
      "3. **Moisturize** with a rich cream to lock in hydration",
      "4. **Apply sunscreen** with at least SPF 30"
    ],
    evening: [
      "1. **Double cleanse** if wearing makeup (oil cleanser followed by gentle cleanser)",
      "2. **Apply treatment** products (like hyaluronic acid serum)",
      "3. **Moisturize** with a richer night cream",
      "4. **Optional:** Apply a facial oil as the final step for extra moisture"
    ],
    weekly: [
      "- **Gentle exfoliation** 1-2 times per week (avoid harsh scrubs)",
      "- **Hydrating mask** 1-2 times per week"
    ],
    tips: [
      "- Use lukewarm (not hot) water when washing your face",
      "- Apply moisturizer while skin is still slightly damp",
      "- Consider using a humidifier in your bedroom",
      "- Drink plenty of water throughout the day",
      "- Avoid alcohol and caffeine, which can dehydrate skin"
    ]
  },
  oily: {
    morning: [
      "1. **Cleanse** with a gentle foaming cleanser",
      "2. **Apply treatment serum** with ingredients like niacinamide or salicylic acid",
      "3. **Moisturize** with a lightweight, oil-free moisturizer",
      "4. **Apply sunscreen** (gel or fluid formula works best)"
    ],
    evening: [
      "1. **Cleanse** thoroughly to remove oil buildup and makeup",
      "2. **Exfoliate** with chemical exfoliants (like BHA) 2-3 times per week",
      "3. **Apply treatment** for specific concerns",
      "4. **Moisturize** with a lightweight formula"
    ],
    weekly: [
      "- **Clay mask** 1-2 times per week to absorb excess oil",
      "- **Chemical exfoliation** 2-3 times per week"
    ],
    tips: [
      "- Don't skip moisturizer (it can actually help regulate oil production)",
      "- Use blotting papers throughout the day instead of adding powder",
      "- Look for 'oil-free' and 'non-comedogenic' on product labels",
      "- Change pillowcases frequently",
      "- Consider using mattifying primers if you wear makeup"
    ]
  },
  normal: {
    morning: [
      "1. **Cleanse** with a gentle cleanser",
      "2. **Apply antioxidant serum** (like vitamin C) for protection",
      "3. **Moisturize** with a medium-weight moisturizer",
      "4. **Apply sunscreen** with SPF 30+"
    ],
    evening: [
      "1. **Cleanse** to remove the day's buildup",
      "2. **Apply treatment products** based on concerns (retinol, peptides, etc.)",
      "3. **Moisturize** to support skin barrier function"
    ],
    weekly: [
      "- **Exfoliate** 1-2 times per week",
      "- **Mask** (based on seasonal needs) once a week"
    ],
    tips: [
      "- Maintain consistency with your routine",
      "- Adjust products seasonally as needed",
      "- Don't forget your neck and décolletage",
      "- Stay hydrated and eat a balanced diet",
      "- Get adequate sleep for skin regeneration"
    ]
  }
};

// Special routines for specific issues
const issueRoutines = {
  acne: {
    additions: [
      "- **AM**: Incorporate benzoyl peroxide (2.5-5%) or salicylic acid treatment",
      "- **PM**: Consider adapalene (Differin) gel - start 2-3 times per week and build up",
      "- Spot treat with benzoyl peroxide or salicylic acid products",
      "- Use lightweight, oil-free products labeled 'non-comedogenic'",
      "- Be patient - acne treatments typically take 6-8 weeks to show significant results"
    ]
  },
  redness: {
    additions: [
      "- Avoid hot water on face - use lukewarm only",
      "- Look for products with centella asiatica, green tea, or licorice root extract",
      "- Skip alcohol-based products and fragrance",
      "- Consider azelaic acid products (morning or evening)",
      "- Always patch test new products before applying to entire face"
    ]
  },
  bags: {
    additions: [
      "- Store eye cream in the refrigerator for extra de-puffing effect",
      "- Use a dedicated eye cream with caffeine or peptides",
      "- Apply with ring finger using gentle tapping motion",
      "- Sleep with head slightly elevated",
      "- Use cold compress in the morning to reduce puffiness"
    ]
  }
};

// General skincare tips and information
const generalInfo = {
  skinTypes: [
    "**Dry skin** produces less sebum than normal skin and lacks lipids needed for moisture retention and protection. It often feels tight, looks dull, and may have flaky patches.",
    "**Oily skin** produces excess sebum, giving a shiny appearance. It's prone to enlarged pores, blackheads, and acne, but often ages well with fewer wrinkles.",
    "**Combination skin** features both oily and dry areas. Typically, the T-zone (forehead, nose, chin) is oily while cheeks are normal to dry.",
    "**Normal skin** is well-balanced, neither too oily nor too dry, with small pores and good circulation."
  ],
  layeringOrder: [
    "1. Cleanser",
    "2. Toner (optional)",
    "3. Treatments/Serums (thinnest to thickest)",
    "4. Eye cream",
    "5. Moisturizer",
    "6. Face oil (PM only)",
    "7. Sunscreen (AM only)"
  ],
  generalTips: [
    "- Consistency is key for skincare results",
    "- Introduce new products one at a time to identify potential reactions",
    "- Most products need 4-6 weeks of consistent use to show results",
    "- Sunscreen is the most effective anti-aging product",
    "- Diet, sleep, and stress levels significantly impact skin health",
    "- It's often better to use fewer, effective products than many different ones"
  ]
};

// Export the knowledge base with utility functions
export const skinKnowledgeBase = {
  // Get a personalized routine based on skin type and issues
  getRoutine(skinType: string, skinIssues: string[] = []): string {
    // In a real implementation, this would be done by the LLM
    // Here we're just demonstrating the concept with a manual implementation
    
    let type = skinType || "normal";
    const routine = routines[type as keyof typeof routines] || routines.normal;
    
    let response = "Here's a daily skincare routine tailored for your specific skin needs! ✨\n\n";
    
    // Morning routine
    response += "🌞 **MORNING ROUTINE**\n\n";
    routine.morning.forEach(step => {
      response += step + "\n";
    });
    response += "\n";
    
    // Evening routine
    response += "🌙 **EVENING ROUTINE**\n\n";
    routine.evening.forEach(step => {
      response += step + "\n";
    });
    response += "\n";
    
    // Weekly treatments
    response += "📆 **WEEKLY TREATMENTS**\n\n";
    routine.weekly.forEach(step => {
      response += step + "\n";
    });
    response += "\n";
    
    // Add specific advice for issues
    skinIssues.forEach(issue => {
      if (issueRoutines[issue as keyof typeof issueRoutines]) {
        response += `✨ **SPECIAL CARE FOR ${issue.toUpperCase()}**\n\n`;
        issueRoutines[issue as keyof typeof issueRoutines].additions.forEach(tip => {
          response += tip + "\n";
        });
        response += "\n";
      }
    });
    
    // Tips
    response += "💡 **HELPFUL TIPS**\n\n";
    routine.tips.forEach(tip => {
      response += tip + "\n";
    });
    
    // Closing
    response += "\nWould you like me to explain any of these steps in more detail or suggest specific products for your routine?";
    
    return response;
  },
  
  // Get product recommendations based on skin type and issues
  getProductRecommendations(skinType: string, skinIssues: string[] = []): string {
    let type = skinType || "normal";
    const products = productsByType[type as keyof typeof productsByType] || productsByType.normal;
    
    let response = "Here are some personalized product recommendations based on your skin analysis! ✨\n\n";
    
    // Cleanser recommendations
    response += "🧴 **CLEANSER RECOMMENDATIONS**\n";
    const cleanser = products.cleansers[Math.floor(Math.random() * products.cleansers.length)];
    response += `• ${cleanser.name} - ${cleanser.description}\n\n`;
    
    // Moisturizer recommendations
    response += "💦 **MOISTURIZER RECOMMENDATIONS**\n";
    const moisturizer = products.moisturizers[Math.floor(Math.random() * products.moisturizers.length)];
    response += `• ${moisturizer.name} - ${moisturizer.description}\n\n`;
    
    // Add issue-specific products
    skinIssues.forEach(issue => {
      if (productsByIssue[issue as keyof typeof productsByIssue]) {
        response += `✨ **FOR ${issue.toUpperCase()}**\n`;
        const product = productsByIssue[issue as keyof typeof productsByIssue][Math.floor(Math.random() * productsByIssue[issue as keyof typeof productsByIssue].length)];
        response += `• ${product.name} - ${product.description}\n\n`;
      }
    });
    
    // Always include sunscreen
    response += "☀️ **SUNSCREEN (ESSENTIAL FOR EVERYONE)**\n";
    const sunscreen = sunscreens[Math.floor(Math.random() * sunscreens.length)];
    response += `• ${sunscreen.name} - ${sunscreen.description}\n\n`;
    
    // Closing
    response += "Would you like more specific information about any of these products? Or would you prefer to see more affordable alternatives?";
    
    return response;
  },
  
  // Get a general response for other queries
  getGeneralResponse(query: string, skinType: string, skinIssues: string[] = []): string {
    // This would be handled by the LLM in a real implementation
    if (query.toLowerCase().includes('yes')) {
      return "Great! I'd be happy to provide more details. What specific aspect of your skincare routine or product recommendations would you like to know more about?";
    } else if (query.toLowerCase().includes('no')) {
      return "No problem at all! If you have any other questions about your skin or skincare routine, I'm here to help!";
    } else {
      return `Based on your ${skinType} skin, I'd recommend focusing on a consistent skincare routine with appropriate products. Would you like me to suggest specific products, a daily routine, or help with a particular skin concern?`;
    }
  }
};