# JSON-LD Schema Markup Examples — Shashi Advanced Health

## LocalBusiness Schema (Homepage)

```json
{
  "@context": "https://schema.org",
  "@type": "MedicalClinic",
  "name": "Shashi Advanced Health",
  "description": "Specialized endocrinology clinic in Bangalore offering expert diabetes, thyroid, PCOS, and hormonal care.",
  "url": "https://www.shashiadvancedhealth.com",
  "telephone": "+91-8884858000",
  "email": "info@shashiadvancedhealth.com",
  "address": [
    {
      "@type": "PostalAddress",
      "streetAddress": "2362, 24th Main Road, Sector 1",
      "addressLocality": "HSR Layout",
      "addressRegion": "Bangalore",
      "postalCode": "560102",
      "addressCountry": "IN"
    }
  ],
  "openingHoursSpecification": {
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
    "opens": "09:00",
    "closes": "20:30"
  },
  "priceRange": "₹₹"
}
```

## Physician Schema (Doctor Profile)

```json
{
  "@context": "https://schema.org",
  "@type": "Physician",
  "name": "Dr. Basavaraj GS",
  "jobTitle": "Senior Consultant Endocrinologist & Diabetologist",
  "description": "DM Endocrinology-certified endocrinologist specializing in diabetes reversal, thyroid treatment, and obesity management.",
  "url": "https://www.shashiadvancedhealth.com/dr-basavaraj-gs",
  "affiliation": {
    "@type": "MedicalOrganization",
    "name": "Shashi Advanced Health"
  },
  "medicalSpecialty": "Endocrinology",
  "qualifications": "MBBS, MD, DM Endocrinology",
  "yearsOfExperience": "10+"
}
```

## FAQPage Schema

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is the difference between an endocrinologist and a diabetologist?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "An endocrinologist specializes in all hormonal disorders. A diabetologist focuses specifically on diabetes management."
      }
    }
  ]
}
```

## How to Implement
1. Add the relevant JSON-LD to each page's <head> or before </body>
2. Validate at https://search.google.com/test/rich-results
3. Test with Google's Rich Results Test tool
4. Monitor in Google Search Console → Enhancements section