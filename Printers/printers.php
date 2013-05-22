<?php

/**
 * Generate list of printers from IST's website. Requires PHP-Curl and PHP-DOM.
 * @author Akshay Joshi <me@akshayjoshi.com>
 */

function getDoc($uri, $data = array())
{
    libxml_use_internal_errors(true);
    $dom = new DOMDocument();
    $dom->loadHTML(fetchDoc($uri, $data));
    return $dom;
}

// UserAgent must be non-Windows for OmniPrint website to be useful.
function fetchDoc($uri, array $data = null, $ua = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.22 (KHTML, like Gecko) Ubuntu Chromium/25.0.1364.160 Chrome/25.0.1364.160 Safari/537.22', $retry = 0)
{
    $curl = curl_init($uri);

    curl_setopt($curl, CURLOPT_FAILONERROR, true);
    curl_setopt($curl, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($curl, CURLOPT_TIMEOUT, 10);
    curl_setopt($curl, CURLOPT_SSL_VERIFYHOST, false);
    curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($curl, CURLOPT_USERAGENT, $ua);

    if (!empty($data)) {
        curl_setopt($curl, CURLOPT_POSTFIELDS, $data);
    }

    $ret = curl_exec($curl);
    if ($ret === false) {
        if ($retry < 3) {
            return fetchDoc($uri, $data, $ua, $retry + 1);
        } else {
            // Curl failed. 3 separate times. Something's pretty messed up.
            die('Something bad happened while CURLing ' . $uri . ' with ' . serialize($data));
        }
    }

    curl_close($curl);
    return $ret;
}

function parsePrinterListPage(DOMDocument $page, array &$printers, $faculty = '')
{
    $forms = $page->getElementsByTagName('form');
    foreach ($forms as $form) {
        // First, gather the hidden input data.

        // This is here so that we can easily convert to CSV later.
        $formData = array(
            'printer' => '',
            'ad' => '',
            'server' => '',
            'comment' => '',
            'driver' => '',
            'room' => '',
            'faculty' => '',
        );
        $inputs = $form->getElementsByTagName('input');
        foreach ($inputs as $input) {
            if ($input->getAttribute('type') === 'hidden') {
                $formData[$input->getAttribute('name')] = $input->getAttribute('value');
            }
        }

        // Validate that the data collected is for a printer (must have
        // an input named 'printer').
        if (!empty($printers[$formData['printer']])) {
            continue;
        }

        // Add the faculty information if we know it, since the page does not
        // provide it.
        $formData['faculty'] = $faculty;

        // Add the printer to our list.
        $printers[$formData['printer']] = array_values($formData);
    }
}

// URL for OmniPrint;
$istUrl = 'http://ist.uwaterloo.ca/cs/omniprint/index.php';

// Fetch the list of faculties and buildings first.
$faculties = array();
$buildings = array();
$printers = array();

// It appears that some printers only show up when queried by building, while
// others only show up when queried by faculty. Therefore, we do both.

// On the page, the list of faculties is in a select box named 'wantfaculty'.
// The rooms select box is named 'wantbuilding'.
$mainPage = getDoc($istUrl);
$selects = $mainPage->getElementsByTagName('select');
foreach ($selects as $select) {
    if ($select->getAttribute('name') === 'wantfaculty') {
        $options = $select->getElementsByTagName('option');
        foreach ($options as $option) {
            $faculties[] = $option->nodeValue;
        }
    }

    if ($select->getAttribute('name') === 'wantbuilding') {
        $options = $select->getElementsByTagName('option');
        foreach ($options as $option) {
            $buildings[] = $option->nodeValue;
        }
    }
}

// For each of the faculties, the printer details are listed on the page as
// hidden inputs.
foreach ($faculties as $faculty) {
    $data = array('wantfaculty' => $faculty);
    $page = getDoc($istUrl, $data);
    // As of April 13th, 2013, each printer is a separate form on the page.
    parsePrinterListPage($page, $printers, $faculty);
}

// Do the same for buildings.
foreach ($buildings as $building) {
    $data = array('wantbuilding' => $building);
    $page = getDoc($istUrl, $data);
    // As of April 13th, 2013, each printer is a separate form on the page.
    parsePrinterListPage($page, $printers);
}

fwrite(STDOUT, 'printer,ad,server,comment,driver,room,faculty' . "\n");
foreach ($printers as $printer) {
    fputcsv(STDOUT, $printer);
}
