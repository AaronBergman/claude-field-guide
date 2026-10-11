# field.awk: print the decoded JSON string field named by -v k=... (needs json.awk).
{ RAW = RAW $0 "\n" }
END { printf "%s", jstr(RAW, k) }
